# CSRNet ağırlığı

`edge` servisi kişi sayımı için CSRNet kullanır. **Ağırlık depoda hazır gelir**
(`csrnet_partB.pth`, 65 MB) — depo klonlandığı gibi çalışır, indirme gerekmez.
Konteyner çalışırken ağa hiç çıkmaz: dosya buradaysa çalışır, yoksa yolu
söyleyip durur.

## Dosya nereden geliyor?

ShanghaiTech **Part B** checkpoint'i, orijinal yazarın deposundan alınmış ve
çıkarım için gereksiz alanlarından arındırılmıştır:

| | Boyut | İçerik |
|---|---|---|
| Ham `.pth.tar` | 130.116.993 bayt | `state_dict` + `epoch` + `optimizer` + `best_prec1` |
| **Depodaki `.pth`** | **65.064.773 bayt** | yalnız `state_dict` (34 tensör) |

`optimizer` state ve `epoch` yalnız eğitime devam etmek için gereklidir;
çıkarımda kullanılmaz. Atılması dosyayı yarıya indirir ve GitHub'ın 100 MB
dosya limitinin altına sokar — Git LFS'e gerek kalmaz.

Kaynak checkpoint bilgisi: `epoch 195`, `best_prec1 (MAE) 9.6879`.

## Ham dosyayı yeniden edinmek

Eğitime devam etmek veya doğrulamak isterseniz:

```bash
curl -L -o partBmodel_best.pth.tar \
  "https://drive.usercontent.google.com/download?id=1zKn6YlLW3Z9ocgPbP99oz7r2nC7_TBXK&export=download&confirm=t"
```

Boyut **130.116.993 bayt** olmalı. Daha küçükse indirme başarısızdır: Google
Drive büyük dosyalar için virüs tarama ara sayfası döndürüyor ve HTML'i hatasız
kaydediyor. `confirm=t` parametresi bunu atlatır. Depodaki indirgenmiş dosyanın
tercih edilme sebebi de budur — sunum günü Drive kotasına ve internete bağımlı
kalınmaz.

`state_dict`'e indirgemek için:

```python
import torch
kontrol = torch.load("partBmodel_best.pth.tar", map_location="cpu", weights_only=False)
torch.save(kontrol["state_dict"], "csrnet_partB.pth")
```

Kod her iki formatı da okur (`csrnet_agi._durum_sozlugu_cikar`), sarılı
checkpoint de çıplak `state_dict` de yüklenir.

## Neden Part B?

Part A yoğun kalabalıklar, Part B seyrek sahneler için eğitilmiştir. Otobüs içi
orta yoğunluktadır ve fark ölçüldüğünde belirgindir — düz gri karede:

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
