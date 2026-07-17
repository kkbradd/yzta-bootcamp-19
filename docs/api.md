# REST & WebSocket

Base: `0.0.0.0:8000`, tüm yollar `/api` prefix'li. Aşağıdaki özet yönlendirme içindir; **kesin alan/şema referansı** her zaman `http://localhost:8000/docs` (Swagger).

## REST uçları (özet)

| Metot | Yol | Ne döner | Veri kaynağı |
|---|---|---|---|
| GET | `/api/saglik` | `{durum, bagimliliklar:{postgres,redis,mqtt}}` — sağlıklıysa 200, değilse 503 | postgres + redis + mqtt görev canlılığı |
| GET | `/api/hatlar` | `list[HatOzeti]` | Karma: liste PostgreSQL, `ortalama_doluluk`/`arac_sayisi` Redis |
| GET | `/api/hatlar/{hat_id}/anlik` | `list[AracAnlikDurumu]` | Tamamen Redis (TTL'i düşen araç atlanır) |
| GET | `/api/hatlar/{hat_id}/trend` | `list[TrendNoktasi]` | Tamamen PostgreSQL |
| GET | `/api/araclar/{arac_id}/olcumler` | `list[OlcumYaniti]` | Tamamen PostgreSQL |
| GET | `/api/cihazlar` | `list[CihazYaniti]` | Karma: liste PostgreSQL, `cevrimici`/`son_gorulme` Redis |
| POST | `/api/hatlar` | `{id:int}` (201) | PostgreSQL — çakışma 409 |
| POST | `/api/araclar` | `{id:int}` (201) | PostgreSQL — çakışma 409 |
| POST | `/api/duraklar` | `{id:int}` (201) | PostgreSQL — çakışma 409 |
| POST | `/api/cihazlar` | `{id:str}` (201) | PostgreSQL — çakışma 409 |
| POST | `/api/atamalar` | `{id:int}` (201) | PostgreSQL — geçersiz referans 409 |
| POST | `/api/oturum` | `{eposta, sifre}` → `{erisim_tokeni}` (JWT); hatalı giriş 401. Panel token'ı localStorage'a yazar | PostgreSQL |

Notlar:
- `trend` query paramları: `baslangic`, `bitis` (zorunlu datetime), `aralik` sadece `saat` veya `15dk` (varsayılan `saat`); başka değer 422.
- `araclar/.../olcumler` query paramları: `baslangic`, `bitis` (zorunlu datetime).
- `POST /api/atamalar` gövdesi discriminated union: `tur` alanı (`hat` | `cihaz`) zorunlu. Cihaz atamasında `arac_id` ile `durak_id`'den **tam biri** dolu olmalı, yoksa 422.
- Cihaz id'leri string (istemci verir); hat/araç/durak/atama id'leri DB üretimi int.

## WebSocket

Uç: `ws://localhost:8000/ws/canli`. İstemci veri göndermez; sadece dinler. İki mesaj tipi:

```jsonc
// Araç güncellemesi
{
  "tip": "arac_guncelleme",
  "arac_id": 1,
  "hat_id": 1,              // int | null — araç güncel bir hatta atanmamışsa null
  "kisi_sayisi": 42,
  "doluluk_orani": 0.47,   // 1.0'a KIRPILMAZ; aşırı doluluk >1.0 olabilir
  "seviye": "orta",        // "seyrek" | "orta" | "yogun"
  "zaman": "2026-07-10T12:00:00+00:00"  // ISO 8601
}

// Cihaz durum değişimi
{
  "tip": "cihaz_durum",
  "cihaz_id": "edge_0001",
  "cevrimici": true,
  "son_gorulme": "2026-07-10T12:00:00+00:00"  // veya null
}
```

`arac_guncelleme` yalnız araç ölçümlerinde yayınlanır; bu dalda `doluluk_orani` ve `seviye` her zaman doludur, `null` gelmez. Araç güncel bir hatta atanmamışsa `hat_id` `null` gelebilir. Durak cihazlarında kapasite yoktur ve durak ölçümü için `arac_guncelleme` **hiç yayınlanmaz** — dolayısıyla `doluluk_orani`/`seviye` null değerleri bu mesajda hiç görünmez.

Kesin kaynak referansı için bkz. `backend/README.md` ve `http://localhost:8000/docs`.

## Asistan servisi

Asistan **ayrı bir servistir** (`:8100`) ve yolları `/api` prefix'i taşımaz.
Ayrıntı: [Asistan](asistan.md).

| Metot | Yol | Ne döner |
|---|---|---|
| POST | `/chat` | `{mesaj}` → `{cevap, tur_sayisi, arac_cagrilari}` |
| GET | `/saglik` | `{durum: "calisiyor"}` |

Panel bu servise ayrı port'tan gittiği için CORS gerekir; izinli origin'ler
`ASISTAN_CORS_IZINLI_ORIGINLER` ile verilir (varsayılan `http://localhost:3000`).
