# CSRNet ağırlığı

`edge` servisi kişi sayımı için CSRNet kullanır. Ağırlık dosyası **depoya dahil
değildir** (~124 MB); bu klasöre elle indirilir. Konteyner çalışırken ağa hiç
çıkmaz — dosya buradaysa çalışır, yoksa yolu söyleyip durur.

## İndirme

```bash
curl -L -o model/partBmodel_best.pth.tar \
  "https://drive.usercontent.google.com/download?id=1zKn6YlLW3Z9ocgPbP99oz7r2nC7_TBXK&export=download&confirm=t"
```

Dosya boyutu **130.116.993 bayt** olmalı. Daha küçükse indirme başarısızdır:
Google Drive büyük dosyalar için virüs tarama ara sayfası döndürüyor ve HTML'i
hatasız kaydediyor. `confirm=t` parametresi bunu atlatır. Yanlış dosya inerse
servis açılışta `torch.load` doğrulamasında anlaşılır bir hatayla durur.

## Neden Part B?

ShanghaiTech Part A yoğun kalabalıklar, Part B seyrek sahneler için eğitilmiştir.
Otobüs içi orta yoğunluktadır ve ölçüldüğünde fark belirgindir — düz gri karede:

| Ağırlık | Tahmin | MAE |
|---|---|---|
| Part A | 7.33 hayalet kişi | 65.90 |
| **Part B** | **0.13** | **9.69** |

Part A'nın taban gürültüsü tek başına sayımı bozar.

## Kalibrasyon uyarısı

İki ağırlık da sokak/tepeden çekim kafa anotasyonlarıyla eğitilmiştir. Yakın
mesafeli, okluzyonlu otobüs içi görüntüsü **dağılım dışıdır**; sistematik sapma
beklenir. Mutlak sayılara güvenmeden önce birkaç kareyi elle sayıp
`EDGE_SAYIM_CARPANI` ile ölçeği düzeltin (ham sayım da loglanır).

## Alternatif kaynaklar

| Kaynak | Boyut | Not |
|---|---|---|
| Drive Part A (`1Z-atzS5Y2pOd-nEWqZRVBDMYJDreGWHH`) | 124 MiB | Yoğun kalabalık için |
| HF `rootstrap-org/crowd-counting` | 62 MiB | README'si "Part B" diyor ama dosya **bit düzeyinde Part A ile aynı** |
| HF `muasifk/CSRNet` | 62 MiB | Üçüncü, ayrı bir eğitim |

Kaynak model: [leeyeehoo/CSRNet-pytorch](https://github.com/leeyeehoo/CSRNet-pytorch)
(Li et al., *CSRNet: Dilated Convolutional Neural Networks for Understanding the
Highly Congested Scenes*, CVPR 2018).
