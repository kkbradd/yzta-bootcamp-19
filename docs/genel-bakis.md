# Genel Bakış

**YOTAY — Otobüs İçi Yoğunluk Tespiti**, toplu taşıma araçlarına ve duraklara yerleştirilen kameralardan gelen görüntülerin görüntü işleme ile analiz edilerek araç/hat/durak bazlı yoğunluk tespiti yapılmasını hedefleyen bir projedir. Amaç, mevcut statik toplu taşıma yapısını daha dinamik ve veriye dayalı bir sisteme dönüştürmek; analiz sonuçlarını yöneticilerin karar süreçlerinde kullanabileceği bir admin panel üzerinden sunmak.

> **Not:** Bu site statik bir proje dokümanıdır. Belgelerdeki `localhost:8000/docs`
> (Swagger), WebSocket ve MQTT adresleri yalnız sistemi yerelde/Docker ile
> çalıştırdığınızda erişilebilir; bu sayfadan tıklandığında çalışmaz.

## Sistemdeki bileşenler

```
edge cihazlar ──MQTT──▶ [ Backend ] ──REST + WebSocket──▶ panel (frontend)
                          ▲     │                             │
                          │     └──▶ [ AI öneri/uyarı motoru ]│
                          │              (yerel LLM)          │
                          │ REST (/api/hatlar...)             │ POST /chat
                          └──────────── [ Asistan ] ◀─────────┘
                                    (OpenJarvis + Ollama)
```

AI tarafı iki parçadır ve **ikisi de varsayılan olarak yereldir**: asistan soruları
yanıtlar, öneri/uyarı motoru arka planda veriyi yorumlar. Her ikisinde de bulut
(Gemini) yalnız açık tercihle devreye girer — bkz. [Öneri & Uyarı Motoru](ai-motoru.md).

| Bileşen | Ne yapar | Kod |
|---|---|---|
| **Edge** | Kameradan yoğunluk ölçümü üretip MQTT'ye yayınlar | `backend/simulator/simulator.py` (referans/sahte yayıncı) |
| **Backend** | MQTT'den ölçüm alır, işler, REST + WebSocket ile sunar | `backend/app/` |
| **Panel (frontend)** | Yöneticinin hat/durak/canlı harita verilerini izlediği arayüz | `frontend/src/` |
| **Asistan** | Panelden gelen soruları backend verisiyle yanıtlayan lokal chatbot (OpenJarvis + Ollama) | `asistan/` — bkz. [Asistan](asistan.md) |
| **AI öneri/uyarı motoru** | Yoğunluk örüntüsünü lokal modelle yorumlayıp operasyonel öneri ve uyarı üretir | `backend/app/adapters/cikan/` — bkz. [Öneri & Uyarı Motoru](ai-motoru.md) |

Tüm sistem tek komutla ayağa kalkar: depo kökünden `docker compose --profile demo up --build`
(servisler: mosquitto, postgres, redis, backend, seed, ollama, asistan, frontend, simulator).
Panel: `http://localhost:3000`.

## Bölümler

| Bölüm | Tür | İçerik |
|---|---|---|
| Genel Bakış | `.md` | Bu sayfa |
| Görsel Özet | `.html` | Modelin ve veri setinin görsel özeti |
| Sistem Mimarisi | `.md` | Heksagonal mimari, katmanlar, bağımlılık yönü |
| REST & WebSocket | `.md` | API uç noktaları ve canlı mesaj şemaları |
| MQTT Sözleşmesi | `.md` | Edge cihaz topic/payload sözleşmesi |
| Asistan | `.md` | Panele bağlı lokal chatbot; tool'lar, `/chat`, Gemini modu |
| Öneri & Uyarı Motoru | `.md` | Yoğunluğu yorumlayan AI motoru; motor seçimi, gizlilik, sağlamlık |
| Ekran Görüntüleri | `.md` | Admin panelinin mevcut sayfaları |

## Yeni sayfa nasıl eklenir?

1. Yeni dosyayı `docs/` klasörüne koy — `.md` ya da `.html` olabilir.
2. `docs/index.html` içindeki `SAYFALAR` listesine bir satır ekle:

```js
{ baslik: "Mimari", dosya: "mimari.md" },
```

Hepsi bu. Menüde otomatik görünür.

> **Not:** Markdown sayfaları tarayıcıda doğrudan dosya olarak açıldığında yüklenmez;
> yerelde `python3 -m http.server` ile önizle. GitHub Pages'te sorunsuz çalışır.
