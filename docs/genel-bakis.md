# Proje Günlüğü

Bu site, **HAT 01 — Otobüs İçi Yoğunluk Tespiti** projesinin süreç dokümantasyonudur.
Yaptığımız işleri adım adım burada topluyoruz; zamanla yeni bölümler eklenecek.

Sol taraftaki panelden bölümler arasında geçebilirsin. İçerikler iki biçimde tutulur:

- **HTML sayfaları** — hazır tasarlanmış görsel özetler (kendi stiliyle açılır)
- **Markdown sayfaları** — bu sayfa gibi hızlı yazılan notlar

## Bölümler

| Bölüm | Tür | İçerik |
|---|---|---|
| Genel Bakış | `.md` | Bu sayfa |
| Görsel Özet | `.html` | Modelin ve veri setinin görsel özeti |

## Yeni sayfa nasıl eklenir?

1. Yeni dosyayı `docs/` klasörüne koy — `.md` ya da `.html` olabilir.
2. `docs/index.html` içindeki `SAYFALAR` listesine bir satır ekle:

```js
{ baslik: "Mimari", dosya: "mimari.md" },
```

Hepsi bu. Menüde otomatik görünür.

> **Not:** Markdown sayfaları tarayıcıda doğrudan dosya olarak açıldığında yüklenmez;
> yerelde `python3 -m http.server` ile önizle. GitHub Pages'te sorunsuz çalışır.
