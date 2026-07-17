# YOTAY Asistan

Yoğunluk verileriyle konuşan, **varsayılan olarak tamamen lokal** chatbot servisi.
Panel kullanıcısı "Şu an en yoğun hat hangisi?" diye sorar; asistan gerçek
Redis/PostgreSQL verisini backend REST API'sinden çekip Türkçe cevaplar.
Varsayılan kurulumda hiçbir veri makineden çıkmaz: LLM (qwen3.5:0.8b) Ollama'da
lokal çalışır, bulut API'si çağrılmaz.

> **Tek istisna:** açıkça Gemini'ye geçerseniz (`ASISTAN_MOTOR=cloud` +
> `GEMINI_API_KEY`) sorular ve yoğunluk verileri Google'a gider. Opsiyoneldir,
> varsayılan değildir — bkz. [Gemini ile çalıştırma](#gemini-ile-çalıştırma-opsiyonel).

## Mimari

```
Kullanıcı → POST /chat → YotayAsistani (OpenJarvis OrchestratorAgent)
                              │  tool çağrıları (function calling)
                              ▼
               hat_yogunluklari / hat_anlik_durum / hat_trend
                              │  GET /api/hatlar...
                              ▼
                      YOTAY backend (8000)          Ollama (qwen3.5:0.8b)
```

- `app/ayarlar.py` — ortam değişkenlerinden okunan ayarlar ve sabitler
- `app/araclar.py` — üç OpenJarvis tool'u; veriyi backend REST API'sinden okur
- `app/cekirdek.py` — agent kurulumu (aşağıdaki reçeteyle) ve `YotayAsistani.sor()`
- `app/servis.py` — FastAPI: `POST /chat`, `GET /saglik`
- `app/model_hazirla.py` — konteyner girişinde modeli Ollama'ya indirir (idempotent)

## Hızlı başlangıç

**Tek komut (önerilen, Docker):** depo kökünden

```bash
docker compose --profile demo up --build     # backend + asistan + Ollama + canlı simülatör
curl -X POST localhost:8100/chat -H "Content-Type: application/json" \
     -d '{"mesaj": "Şu an hatlarda yoğunluk nasıl?"}'
```

İlk açılışta model (~1 GB) indirilir ve `ollama_modelleri` volume'unda kalır;
sonraki açılışlar beklemesizdir.

**Yerel geliştirme:** Ollama kurulu ve backend ayakta iken

```bash
cd asistan
uv sync
uv run uvicorn app.servis:uygulama --port 8100
```

## Ortam değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `YOTAY_API_ADRESI` | `http://localhost:8000` | Backend REST API adresi |
| `OLLAMA_ADRESI` | `http://localhost:11434` | Ollama sunucusu |
| `ASISTAN_MODEL` | `qwen3.5:0.8b` | Kullanılacak model (örn. `qwen3.5:9b` ile yükseltilebilir) |
| `ASISTAN_MOTOR` | `ollama` | OpenJarvis çıkarım motoru (`llamacpp` vb. lokal motorlar; `cloud` yalnız Gemini için) |
| `GEMINI_API_KEY` | _(boş)_ | Yalnız Gemini modunda gerekir; `GOOGLE_API_KEY` de kabul edilir |

`ASISTAN_MOTOR` ve `ASISTAN_MODEL` aynı kararı kodlar; tutarsız kombinasyonlar
(örn. `cloud` + `gpt-4o`, ya da `gemini-3-flash` + `ollama`) açılışta reddedilir.
Sebebi: OpenJarvis böyle bir tutarsızlıkta hata vermeyip sessizce lokal motora düşer.

## Gemini ile çalıştırma (opsiyonel)

qwen3.5:0.8b'nin cevap kalitesi yetmiyorsa aynı tool'larla Gemini'ye geçebilirsiniz.

> ⚠️ **Gizlilik:** Bu modda sorular **ve tool sonuçları — yani gerçek yoğunluk
> verileriniz —** Google'a gider. Projenin "veri makineden çıkmaz" garantisi yalnız
> varsayılan lokal modda geçerlidir. Ayrıca Gemini ücretlidir (kullandıkça öde).

```bash
# depo kökünde .env (git'e girmez, kök .gitignore'da)
ASISTAN_MOTOR=cloud
ASISTAN_MODEL=gemini-3-flash
GEMINI_API_KEY=...
```

```bash
docker compose --profile demo up --build   # .env otomatik okunur
```

Yerel geliştirmede: `uv sync --extra gemini` (Docker imajında zaten kurulu).

Desteklenen modeller (OpenJarvis `cloud` motoru): `gemini-3-flash`, `gemini-3-pro`,
`gemini-2.5-flash`, `gemini-2.5-pro`. Sağlayıcı **model adından** seçilir — adında
"gemini" geçmesi yeterlidir.

**Reçete neden değişmiyor?** OpenJarvis'in Gemini yolu (`engine/cloud.py`
`_generate_google`) mesajlardaki SYSTEM rolünü alıp `system_instruction`'a koyar ve
tool'ları `function_declarations`'a çevirir — yani aşağıdaki reçete ve `araclar.py`
Gemini'de de aynen çalışır. Kısa prompt zorunluluğu 0.8b'ye özgüydü; Gemini'de o
baskı yok ama prompt aynı kalabilir.

**Anahtar unutulursa ne olur?** Servis açılışta net bir Türkçe hatayla durur. Bu
kasıtlıdır: OpenJarvis anahtar yokken sessizce lokal modele düşer (`CloudEngine.health()`
False → `get_engine` fallback) ve Gemini beklerken qwen'den cevap alırdınız.

## API

`POST /chat` → `{"mesaj": "34 hattında durum ne?"}`

```json
{
  "cevap": "34 hattında şu an durum:\n* Araç 1: 48 kişi, doluluk %53, seviye orta...",
  "tur_sayisi": 2,
  "arac_cagrilari": ["hat_anlik_durum"]
}
```

`GET /saglik` → `{"durum": "calisiyor"}`

## Kritik notlar: küçük modelle güvenilir tool çağırma reçetesi

qwen3.5:0.8b ile function calling **kırılgandır**; aşağıdaki üçlü deneysel olarak
doğrulanmıştır ve `cekirdek.py`'de kodludur:

1. **Sistem promptu `AgentContext` konuşmasına SYSTEM mesajı olarak konur.**
   OpenJarvis'in `OrchestratorAgent(system_prompt=...)` parametresi, varsayılan
   function_calling modunda yok sayılır (bug; `_run_function_calling` promptu
   `_build_messages`'a iletmez) ve config'in İngilizce varsayılan promptu devreye
   girip tool çağırmayı bozar.
2. **`temperature=0.0`** — 0.7'de tool çağırma yazı-tura gibi rastgeleleşir.
3. **Sistem promptu ÇOK KISA tutulur.** Canlı tarama sonucu: 2 cümlelik sert
   prompt + tool adları 2/2 tool çağırttı; aynı prompta tek cümle eklemek bile
   0/2'ye düşürdü. `SISTEM_PROMPTU`'yu genişletmeden önce varyant testini tekrarlayın.

Diğer notlar:

- **OpenJarvis SHA-pinli** kurulur (`pyproject.toml`); bug düzelirse pin
  güncellenip 1. madde sadeleştirilebilir. Kurulum Rust istemez (Rust eklentisi
  yalnız kullanmadığımız memory backend'leri içindir).
- **Gizlilik:** OpenJarvis'in anonim kullanım analitiği bizim kod yolumuzda hiç
  başlatılmaz; `cekirdek._motor_kur` yine de `analytics.enabled=False` ile açıkça
  kapatır. Telemetri (token/latency) yalnız lokal SQLite'a yazılır.
- Model cevapları 0.8b sınırları içinde değerlendirilmeli; daha akıcı cevap için
  `ASISTAN_MODEL=qwen3.5:9b` yeterlidir (aynı reçete geçerli).

## Test

```bash
uv run pytest              # birim testler (ağ/model gerekmez, ~1 sn)
uv run ruff check .
uv run pytest tests/entegrasyon -m entegrasyon   # backend + Ollama ayaktayken
```

Birim testler `Sahte*` fake'lerle çalışır (backend idiomu): tool'lar
`httpx.MockTransport`, agent `SahteMotor`, HTTP katmanı `TestClient` + sahte asistan.
