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
│  ├─ api/
│  │  ├─ client.js        # VITE_API_URL tabanlı fetch sarmalayıcı
│  │  └─ hatlar.js        # hatlariGetir() + backend seviye eşlemesi
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

Backend adresi **derleme anında** gömülür: `import.meta.env.VITE_API_URL` (varsayılan `http://localhost:8000`). Çalışma anında değiştirilemez — farklı bir backend için yeniden build gerekir.

Sayfa bazında veri kaynağı:

| Sayfa | Veri kaynağı |
|---|---|
| `LinesPage` (Hatlar) | Gerçek backend verisi — `src/api/hatlar.js` → `GET /api/hatlar`. Backend'e erişilemezse mock diziye (`DEMO_HATLAR`) düşer. |
| `DashboardPage`, `LiveMapPage`, `StopsPage` | Şu an mock/statik veri. Backend'e henüz bağlı değil. |

`hatlar.js`, backend'in seviye isimlerini (`seyrek`/`orta`/`yogun`) arayüzün kullandığı isimlere (`dusuk`/`orta`/`yuksek`) çevirir; backend'de olmayan alanlar (`duration`, `stops`) `—` ile gösterilir.

---

## Docker ile çalıştırma

Üretim derlemesini nginx ile servis eder (multi-stage: Vite build → nginx statik sunum).

```bash
docker compose up --build
# → http://localhost:3000
```

- Tarayıcı origin'i `http://localhost:3000` olur; backend'in CORS ayarı (`CORS_IZINLI_ORIGINLER`) bu origin'e varsayılan olarak izin verir.
- Backend adresi **derleme anında** gömülür: `VITE_API_URL` (varsayılan `http://localhost:8000`). Farklı bir backend için `docker-compose.yml` içindeki `args.VITE_API_URL`'i değiştirip yeniden build et.
- **İki bağımsız stack:** Bu compose yalnız frontend'i ayağa kaldırır. Backend ayrı `backend/docker-compose.yml` ile çalışır; aralarında Docker network köprüsü yoktur — frontend container'ı backend'e tarayıcı üzerinden (`fetch`) bağlanır, aradaki köprüyü CORS kurar.
- Backend'in ayakta olması yetmez, **seed** de gerekir (`python -m app.seed`) — aksi halde Hatlar sayfası boş liste gösterir (hata değil, normal davranış).

---

## Sık takılınan yerler

- **`VITE_API_URL` derleme anında gömülür.** Runtime'da ortam değişkeni değiştirmek işe yaramaz; farklı backend adresi için imajı yeniden build et.
- **Routing kütüphanesi yok.** `App.jsx`, `useState` ile hangi sayfanın gösterileceğini tutar; URL değişmiyor, tarayıcı geri/ileri tuşları ve deep-link çalışmıyor. İleride `react-router` eklenmesi planlanabilir.
- **`package.json` adı hâlâ `temp-react`.** create-vite şablonundan kalma, henüz özelleştirilmedi.
- **Dashboard/LiveMap/Stops sayfaları mock veri kullanıyor.** Backend'de veri değiştirse bile bu sayfalarda görünmez — henüz `LinesPage` dışında API bağlantısı yok.
- **Oxlint `react/rules-of-hooks` zorunlu** (`.oxlintrc.json`). Hook kurallarını çiğneyen kod `npm run lint`'te hata verir.

---

## Kararlar & kapsam dışı

- **Auth yok.** `LoginPage` state tutar ama gerçek kimlik doğrulama yapmaz.
- **Routing/state yönetim kütüphanesi yok (henüz).** Sayfa geçişleri ve veri `useState`/`useEffect` ile local tutuluyor.
