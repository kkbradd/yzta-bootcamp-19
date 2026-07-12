# Genel Bakış

**YOTAY — Otobüs İçi Yoğunluk Tespiti**, toplu taşıma araçlarına ve duraklara yerleştirilen kameralardan gelen görüntülerin görüntü işleme ile analiz edilerek araç/hat/durak bazlı yoğunluk tespiti yapılmasını hedefleyen bir projedir. Amaç, mevcut statik toplu taşıma yapısını daha dinamik ve veriye dayalı bir sisteme dönüştürmek; analiz sonuçlarını yöneticilerin karar süreçlerinde kullanabileceği bir admin panel üzerinden sunmak.

## Sistemdeki bileşenler

```
edge cihazlar ──MQTT──▶ [ Backend ] ──REST + WebSocket──▶ panel (frontend)
```

| Bileşen | Ne yapar | Kod |
|---|---|---|
| **Edge** | Kameradan yoğunluk ölçümü üretip MQTT'ye yayınlar | `backend/simulator/simulator.py` (referans/sahte yayıncı) |
| **Backend** | MQTT'den ölçüm alır, işler, REST + WebSocket ile sunar | `backend/app/` |
| **Panel (frontend)** | Yöneticinin hat/durak/canlı harita verilerini izlediği arayüz | `frontend/src/` |

## Bölümler

| Bölüm | Tür | İçerik |
|---|---|---|
| Genel Bakış | `.md` | Bu sayfa |
| Görsel Özet | `.html` | Modelin ve veri setinin görsel özeti |
| Sistem Mimarisi | `.md` | Heksagonal mimari, katmanlar, bağımlılık yönü |
| REST & WebSocket | `.md` | API uç noktaları ve canlı mesaj şemaları |
| MQTT Sözleşmesi | `.md` | Edge cihaz topic/payload sözleşmesi |
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
