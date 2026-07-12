# Ekran Görüntüleri

HAT 01 admin panelinin (frontend) mevcut sayfaları.

## Giriş

![Giriş sayfası](assets/ekranlar/login-page.png)

Split-screen giriş ekranı. Şu an gerçek kimlik doğrulama yapmaz, panele geçiş için placeholder.

## Kontrol Paneli

![Kontrol paneli](assets/ekranlar/dashboard.png)

Hat bazlı doluluk trendlerini Recharts ile gösteren genel özet ekranı. Zaman aralığı (12s/24s/3g/7g/30g) ve hat filtresi destekler.

## Canlı Harita

![Canlı harita](assets/ekranlar/live-map.png)

Araçların anlık konum ve doluluk durumunu haritada gösteren sayfa.

## Hatlar

![Hatlar sayfası](assets/ekranlar/lines.png)

Backend'e bağlı tek sayfa — `GET /api/hatlar`'dan gerçek veri çeker (hat no, güzergah, ortalama doluluk, araç sayısı). Backend'e erişilemezse demo veriye düşer.

## Duraklar

![Duraklar sayfası](assets/ekranlar/stops.png)

Durak listesi, arama/filtreleme ve erişilebilirlik/wifi/dijital ekran bilgisi.

---

Kaynak kod: `frontend/src/pages/`. Sayfa bazında hangi verinin gerçek/mock olduğu için bkz. `frontend/README.md` → API entegrasyonu.
