# Veri Metodolojisi

Sistemdeki sayıların nereden geldiği. İki ayrı kalibrasyon var; ikisi de tahminle
değil, ölçümle yapıldı:

| Ne | Kaynak | Sonuç |
|---|---|---|
| **Mock yoğunluk eğrisi** | İBB Saatlik Toplu Ulaşım Veri Seti (BELBİM akbil) | 24 saatlik hafta içi/hafta sonu çarpanları |
| **CSRNet sayım ölçeği** | `otobus.mp4`'ün elle sayılmış referansı | `EDGE_SAYIM_CARPANI = 0.78` |

---

## 1. Mock yoğunluk eğrisi

Demo verisinin gerçekçi olması için saatlik doluluk çarpanları uyduruldu değil,
İstanbul'un açık akbil verisinden türetildi.

### Kaynak

[İBB Saatlik Toplu Ulaşım Veri Seti](https://data.ibb.gov.tr/dataset/hourly-public-transport-data-set)
— BELBİM akbil işlemlerinin saat bazında toplulaştırılmış hâli.

> **Tuzak:** Veri portalının CKAN API önizlemesi yalnız **99 satır** döner. Gerçek
> analiz için ham CSV dosyalarının indirilip akış hâlinde işlenmesi gerekir;
> önizlemeye bakıp "veri bu kadar" sanılmamalı.

### Adım adım

**1. Gün seçimi.** Aylık CSV'ler örneklenmiş — çoğu gün yalnız parça içeriyor. Tam
24 saati olan günler ayıklandı:

- **Hafta içi:** 2, 4, 16, 17, 18 Ekim 2024 (5 tam gün)
- **Hafta sonu:** 1 Eylül 2024 (Pazar)

**2. Üsküdar filtresi.** Hat adında `USKUDAR` geçen kayıtlar alındı.

| | Şehir geneli otobüs binişi | Üsküdar hatları |
|---|---|---|
| Hafta içi (gün ort.) | 4.190.000 | 171.438 |
| Pazar | 1.900.000 | 76.828 |

**3. Saatlik dağılım** çıkarıldı ve zirve saati 1.0 kabul edilerek normalize edildi.

**4. Akış → stok yumuşatma.** Kart basma **binişi** ölçer; doluluk ise *araç içindeki*
yolcudur — biniş anından sonra da devam eder ve saat sınırlarında keskin sıçramaz.
Her saat komşularıyla harmanlandı:

```
düzeltilmiş(s) = 0.25 × ham(s-1) + 0.55 × ham(s) + 0.20 × ham(s+1)
```

**5. Gece tabanı 0.06.** Ham veride gece saatleri sıfıra yakın, ama Üsküdar'da gerçek
gece servisi var (**11ÜS** Sultanbeyli–Üsküdar). Boş otobüs göstermek yanıltıcı olurdu.

**6. Zirve 1.15'e ölçeklendi** — oturma kapasitesinin %15 üstü, yani ayakta yolcu.

### Sonuç

`backend/app/gecmis_veri_yukle.py` içindeki tablolar:

```python
HAFTA_ICI_CARPANLARI = (
    0.06, 0.06, 0.06, 0.06, 0.06, 0.18, 0.62, 1.15, 1.15, 0.84, 0.67, 0.67,
    0.75, 0.83, 0.91, 1.07, 1.14, 1.11, 1.03, 0.83, 0.56, 0.38, 0.26, 0.14,
)
HAFTA_SONU_CARPANLARI = (
    0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.11, 0.18, 0.24, 0.25, 0.26, 0.31,
    0.41, 0.46, 0.49, 0.50, 0.52, 0.54, 0.53, 0.49, 0.41, 0.31, 0.23, 0.13,
)
```

Üretilen veritabanı verisinin gerçek profili (60 kişilik araç):

```
07:00 ███████████████████████████████████  62 kişi   ← keskin sabah zirvesi
16:00 ███████████████████████████          57 kişi   ← geniş akşam platosu
03:00 █                                     3 kişi   ← gece (sıfır değil)
```

### Veriden çıkan üç bulgu

**Sabah zirvesi keskin, akşam platosu geniş.** 07:00 günün tek en yoğun saati
(Üsküdar günlük binişlerinin %9.6'sı). Akşam ise 15:00–18:00 arası **plato** —
sivri bir tepe değil. Zirve saat başına daha yoğun olsa da, **akşam platosu toplamda
daha fazla yolcu taşıyor.**

**Öğle çukuru yok.** Gün ortası hiçbir saat zirvenin ~%50'sinin altına inmiyor.

**Hafta sonu, ölçeklenmiş bir iş günü DEĞİL.** Ham veride Pazar toplamı iş gününün
%44.8'i (tablolardaki düzeltilmiş hâliyle %46), ama sabah zirvesi **tamamen kayboluyor**
(Pazar 07:00 = 0.18 ↔ hafta içi 1.15, ~6 kat fark). Geriye tek bir tembel öğleden sonra
tümseği kalıyor (zirve 17:00). "Hafta içi × 0.5" diye modellemek yanlış olurdu.

### Bilinen sınırlar

| Sınır | Ayrıntı |
|---|---|
| **Zirve 1.15 ölçülmedi** | Açık veri **biniş** verir, doluluk oranı değil. 1.15 kalibre edilmiş bir seçim. İETT'nin gerçek doluluk sensörü var (Traffix, 125 metrobüs) ama verisi açık değil. |
| **Hafta sonu tek güne dayanıyor** | Yalnız 1 Eylül 2024 Pazar. Cumartesi muhtemelen biraz daha yüksek. |
| **Üsküdar filtresi yaklaşık** | Hat adına göre eşleşme; ilçeden geçen hatları da kapsıyor. `town` alanı yalnız raylı/deniz satırlarında dolu. |

### Yardımcı bulgular

Üsküdar aktarma merkezi büyüklüğü (basından, İBB/TCDD verisine dayalı):
Marmaray Üsküdar **63.960 yolcu/gün** (İstanbul'un 2. en yoğun istasyonu),
M5 Üsküdar **50.305/gün** (6.).

En yoğun Üsküdar otobüs hatları: **15B** (%15.4), **12A** (%10.1), **16F** (%8.0),
**320A** (%6.3) — hat bazlı ağırlıklandırma istenirse kullanılabilir.

İETT araç kapasiteleri (resmî/ihale belgeleri): solo dizel **100**, solo elektrikli
**80**, körüklü **150**, midibüs **60**, metrobüs **280**. Oturan/ayakta ayrımı
yayımlanmıyor. *(Projede tüm araçlar 60 kapasiteli tutuldu — doluluk hesapları tek
kapasite üzerinden tutarlı kalsın diye kasıtlı.)*

---

## 2. CSRNet sayım kalibrasyonu

CSRNet sokak/tepeden çekim kafa anotasyonlarıyla eğitilmiştir. Yakın mesafeli,
okluzyonlu **otobüs içi görüntüsü dağılım dışıdır** — sistematik sapma beklenir.

### Yöntem

Demo videosunun (`otobus.mp4`, 45 sn) **her saniyesi elle sayıldı** (referans:
ortalama 4.1, en fazla 8 kişi). Aynı saniyelerdeki kareler CSRNet'e verilip ham
çıktıyla karşılaştırıldı; ölçek çarpanı en küçük kareler ile bulundu.

### Sonuç

| Ölçüt | Değer |
|---|---|
| **Korelasyon (ham ↔ gerçek)** | **0.88** |
| Ham sayım ortalaması | 5.43 (gerçek: 4.11 — sistematik fazla sayım) |
| MAE, çarpansız | 1.64 kişi |
| MAE, çarpan uygulanmış | **1.06 kişi** |
| En küçük kareler çarpanı | **0.78** |

**Yorum:** Yüksek korelasyon, modelin insan sayısındaki *değişimi* doğru takip
ettiğini gösteriyor — yalnızca ölçeği kayıktı. Bu yüzden tek bir çarpan düzeltmesi
yeterli oldu.

> Çarpan bu videoya özeldir. **Başka bir video veya kamera açısı için yeniden
> ölçülmelidir.** Ham sayım `DEBUG` seviyesinde loglanır, böylece çarpanın etkisi
> ayırt edilebilir.

### Bilinen sınır

Videonun son saniyelerinde gerçek sayım 0'a inerken CSRNet ~1.5 gösteriyor (boş
sahnede küçük halüsinasyon). Zararsız: `csrnet_kestirim.py` negatif/aşırı düşük
değerleri sıfıra kırpıyor.

---

## Yeniden üretme

```bash
# Mock veriyi yeni eğriyle yeniden üret
docker compose exec postgres psql -U hat01 -d hat01 \
    -c "DELETE FROM olcumler WHERE sira_no < 0;"
docker compose up gecmis_veri_yukle

# Eğri testleri (zirve/gece/hafta sonu davranışı)
cd backend && uv run pytest tests/unit/test_gecmis_veri_carpanlari.py
```

## Kaynaklar

- [İBB Saatlik Toplu Ulaşım Veri Seti](https://data.ibb.gov.tr/dataset/hourly-public-transport-data-set) — birincil kaynak
- [İETT Otobüs Filosu](https://iett.istanbul/icerik/otobus-filosu)
- [İETT Gece Hatları](https://iett.istanbul/icerik/gece-hatlari)
- [Marmaray yolcu sayıları](https://marmaray.istanbul/marmaray-yolcu-sayilari/)
