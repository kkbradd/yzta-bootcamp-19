# HAT 01 Frontend

Backend'in REST uçlarını tüketen, otobüs hattı/durak/canlı harita verilerini yöneticiye gösteren React + Vite admin paneli.

Sistemdeki yeri:

```
[ HAT 01 Backend ] ──REST + WebSocket──▶ [ Panel (frontend) ]
```

---

## Nereden başlamalı?

- **Sadece paneli çalıştıracaksan:** [Hızlı başlangıç](#hızlı-başlangıç) yeter. Backend'in ayrı çalışıyor olması gerekir (bkz. `backend/README.md`).
- **Docker ile prod benzeri çalıştıracaksan:** [Docker ile çalıştırma](#docker-ile-çalıştırma).
- **Yeni sayfa/bileşen ekleyeceksen:** [Proje yapısı](#proje-yapısı) ve [API entegrasyonu](#api-entegrasyonu) bölümlerine bak.

---

## Hızlı başlangıç

`frontend/` dizininden:

```bash
npm install
npm run dev        # → http://localhost:5173
```

Backend'in `http://localhost:8000`'de ayrıca çalışıyor olması gerekir (`backend/README.md` → Hızlı başlangıç). Varsayılan `VITE_API_URL=http://localhost:8000` kullanılır; backend'in CORS ayarı `localhost:5173`'e zaten izin verir, ek yapılandırma gerekmez.

---

## Script'ler

| Komut | Ne yapar |
|---|---|
| `npm run dev` | Vite dev server, HMR ile (`:5173`) |
| `npm run build` | Üretim derlemesi (`dist/`) |
| `npm run preview` | `build` çıktısını yerelde önizler |
| `npm run lint` | Oxlint ile statik analiz |

---

## Proje yapısı

```
frontend/
├─ src/
│  ├─ pages/             # LoginPage, DashboardPage, LiveMapPage, LinesPage, StopsPage
│  ├─ components/
│  │  └─ AsistanWidget.jsx # sağ altta yüzen sohbet paneli (asistan servisi)
│  ├─ api/
│  │  ├─ client.js        # VITE_API_URL / VITE_ASISTAN_URL tabanlı fetch sarmalayıcı
│  │  ├─ hatlar.js        # hatlariGetir() + backend seviye eşlemesi
│  │  └─ asistan.js       # asistanaSor() → POST /chat
│  ├─ hooks/
│  │  └─ useClock.js      # saniyede güncellenen tr-TR saat
│  └─ App.jsx              # sayfa yönlendirme (useState tabanlı, react-router yok)
├─ Dockerfile              # multi-stage: Vite build → nginx statik sunum
├─ nginx.conf              # SPA fallback + gzip
├─ docker-compose.yml       # port 3000:80
└─ vite.config.js
```

---

## API entegrasyonu

Servis adresleri **derleme anında** gömülür — çalışma anında değiştirilemez, farklı adres için yeniden build gerekir:

| Değişken | Varsayılan | Servis |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend REST API |
| `VITE_ASISTAN_URL` | `http://localhost:8100` | Asistan (chatbot) servisi |

Bu adresler **tarayıcının göreceği** adreslerdir; Docker ağı içindeki servis adları (`backend:8000`) değil — kodu çalıştıran tarayıcı o ağın dışındadır.

Sayfa bazında veri kaynağı:

| Sayfa | Veri kaynağı |
|---|---|
| `LinesPage` (Hatlar) | Gerçek backend verisi — `src/api/hatlar.js` → `GET /api/hatlar`. Backend'e erişilemezse mock diziye (`DEMO_HATLAR`) düşer. |
| `AsistanWidget` (her sayfada) | Asistan servisi — `src/api/asistan.js` → `POST /chat`. Servise ulaşılamazsa sohbette açıklayıcı hata balonu gösterir. |
| `DashboardPage`, `LiveMapPage`, `StopsPage` | Şu an mock/statik veri. Backend'e henüz bağlı değil. |

`hatlar.js`, backend'in seviye isimlerini (`seyrek`/`orta`/`yogun`) arayüzün kullandığı isimlere (`dusuk`/`orta`/`yuksek`) çevirir; backend'de olmayan alanlar (`duration`, `stops`) `—` ile gösterilir.

### Asistan (chatbot)

Panelin sağ altındaki 💬 düğmesi sohbeti açar; oturum açıldıktan sonra her sayfada bulunur. Cevaplar lokal LLM'den geldiği için birkaç saniye sürebilir (varsayılan kurulumda veri makineden çıkmaz — bkz. [asistan/README.md](../asistan/README.md)).

Asistan ayrı port'ta (8100) olduğu için tarayıcı CORS ister; asistan servisi `ASISTAN_CORS_IZINLI_ORIGINLER` ile panelin origin'ine izin verir (varsayılan `http://localhost:3000`). Panel farklı bir port/origin'de sunulacaksa o değişkeni de güncelleyin, yoksa tarayıcı istekleri bloklar.

---

## Docker ile çalıştırma

**Tüm sistem tek komutla (önerilen):** depo kökünden — backend, asistan, Ollama, veritabanları ve panel birlikte kalkar, seed otomatik çalışır.

```bash
docker compose --profile demo up --build   # + canlı simülatör verisi
# → panel http://localhost:3000
```

**Yalnız frontend:** üretim derlemesini nginx ile servis eder (multi-stage: Vite build → nginx statik sunum).

```bash
docker compose up --build
# → http://localhost:3000
```

- Tarayıcı origin'i `http://localhost:3000` olur; backend'in (`CORS_IZINLI_ORIGINLER`) ve asistanın (`ASISTAN_CORS_IZINLI_ORIGINLER`) CORS ayarları bu origin'e varsayılan olarak izin verir.
- Adresler **derleme anında** gömülür: `VITE_API_URL`, `VITE_ASISTAN_URL`. Farklı adres için `docker-compose.yml` içindeki `args`'ı değiştirip yeniden build et.
- **Bağımsız stack'ler:** Bu compose yalnız frontend'i ayağa kaldırır; backend/asistan ayrı çalışır. Aralarında Docker network köprüsü yoktur — panel onlara tarayıcı üzerinden (`fetch`) bağlanır, aradaki köprüyü CORS kurar.
- Backend'in ayakta olması yetmez, **seed** de gerekir (`python -m app.seed`) — aksi halde Hatlar sayfası boş liste gösterir (hata değil, normal davranış). Kök compose bunu kendisi yapar.

---

## Sık takılınan yerler

- **`VITE_API_URL` / `VITE_ASISTAN_URL` derleme anında gömülür.** Runtime'da ortam değişkeni değiştirmek işe yaramaz; farklı adres için imajı yeniden build et.
- **Sohbet "Asistana ulaşılamadı" diyorsa** önce asistan ayakta mı bak (`curl localhost:8100/saglik`), sonra CORS: panel farklı bir origin'den sunuluyorsa asistanın `ASISTAN_CORS_IZINLI_ORIGINLER` değişkenine o origin'i ekle. Tarayıcı konsolunda CORS hatası görünür, ağ sekmesinde istek "blocked" olur.
- **Asistan cevabı birkaç saniye sürer.** Lokal LLM (qwen3.5:0.8b) çıkarımı yavaştır; widget bu sırada "Düşünüyor…" gösterir, donma değildir.
- **Routing kütüphanesi yok.** `App.jsx`, `useState` ile hangi sayfanın gösterileceğini tutar; URL değişmiyor, tarayıcı geri/ileri tuşları ve deep-link çalışmıyor. İleride `react-router` eklenmesi planlanabilir.
- **`package.json` adı hâlâ `temp-react`.** create-vite şablonundan kalma, henüz özelleştirilmedi.
- **Dashboard/LiveMap/Stops sayfaları mock veri kullanıyor.** Backend'de veri değiştirse bile bu sayfalarda görünmez — henüz `LinesPage` dışında API bağlantısı yok.
- **Oxlint `react/rules-of-hooks` zorunlu** (`.oxlintrc.json`). Hook kurallarını çiğneyen kod `npm run lint`'te hata verir.

---

## Kararlar & kapsam dışı

- **Auth yok.** `LoginPage` state tutar ama gerçek kimlik doğrulama yapmaz.
- **Routing/state yönetim kütüphanesi yok (henüz).** Sayfa geçişleri ve veri `useState`/`useEffect` ile local tutuluyor.
