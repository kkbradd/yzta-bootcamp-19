# YOTAY Edge — video → CSRNet → MQTT

Otobüs içi kamera görüntüsünden kişi sayısı üretip MQTT'ye yayınlayan edge cihaz
servisi. Kamera yerine bir **video dosyası** okur; dosya sona gelince başa sarar.

Yayın sözleşmesi `docs/mqtt.md`'dir; backend tarafında hiçbir değişiklik
gerekmez — servis, `simulator.py` ile aynı topic ve şemayı kullanır.

```
video → kare → CSRNet → kişi sayısı → filo/edge_0001/yogunluk → backend → panel
```

## Çalıştırma

```bash
# Depo kökünden — modelsiz, boru hattını denemek için:
EDGE_MOTOR=sahte docker compose --profile gercek up --build

# Gerçek modelle (video ve ağırlık hazırsa):
docker compose --profile gercek up --build
```

> **`simulator` ile aynı anda çalıştırmayın.** İkisi de `edge_0001` adına yayın
> yapar ve `sira_no`'yu aynı saat tohumundan üretir; çakışan ölçümler backend'de
> `UNIQUE(cihaz_id, sira_no)` kısıtına takılıp **sessizce** yutulur. `demo` ve
> `gercek` profilleri ayrı olduğu için varsayılan kullanımda bu mümkün değildir.

## Kurulum

**1. Video.** Dosyayı `edge/videolar/` altına koyun ve yolu ayarlayın:

```bash
cp ~/otobus_ici.mp4 edge/videolar/otobus.mp4
```

Varsayılan yol `/uygulama/videolar/otobus.mp4`; başka isim kullanacaksanız
`EDGE_VIDEO_YOLU` ile bildirin. Videolar depoya girmez (`.gitignore`).

**2. Model ağırlığı.** `model/README.md`'deki talimatla `model/` altına indirin.
Konteyner çalışırken **ağa hiç çıkmaz**: dosya oradaysa çalışır, yoksa yolu
söyleyip durur.

## Ortam değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `EDGE_MOTOR` | `csrnet` | `csrnet` veya `sahte` |
| `EDGE_VIDEO_YOLU` | `/uygulama/videolar/otobus.mp4` | Okunacak video |
| `EDGE_AGIRLIK_YOLU` | `/uygulama/model/partBmodel_best.pth.tar` | CSRNet ağırlığı |
| `EDGE_CIHAZ_ID` | `edge_0001` | Yayın yapılan cihaz kimliği |
| `EDGE_BROKER` / `EDGE_PORT` | `localhost` / `1883` | MQTT broker |
| `EDGE_YAYIN_PERIYODU_SN` | `2.0` | İki ölçüm arası süre |
| `EDGE_SAYIM_CARPANI` | `1.0` | Kalibrasyon çarpanı (aşağıya bakın) |
| `EDGE_GENISLIK` / `EDGE_YUKSEKLIK` | `480` / `360` | Modele verilecek kare boyutu |
| `EDGE_IS_PARCACIGI` | `4` | torch iş parçacığı sayısı |

Tutarsız yapılandırma **açılışta** yakalanır: geçersiz motor, eksik video, eksik
ağırlık ve sıfır periyot, yığın izi yerine ne yapılacağını söyleyen tek satırla
servisi durdurur.

## Kalibrasyon

CSRNet sokak/tepeden çekim kafa anotasyonlarıyla eğitilmiştir. Yakın mesafeli,
okluzyonlu otobüs içi görüntüsü **dağılım dışıdır** ve sistematik sapma beklenir.

Birkaç kareyi elle sayıp `EDGE_SAYIM_CARPANI` ile ölçeği düzeltin. Ham sayım da
loglanır (`DEBUG` seviyesinde), böylece çarpanın etkisi ayırt edilebilir.

`edge_0001` seed'de **kapasite 90** olan `34 HAT 001` aracına atanmıştır; seviye
eşikleri bu kapasiteye göre: **<36** seyrek, **36–63** orta, **>63** yoğun.

## Performans

CSRNet CPU'da ölçülen süreler (girdi boyutuna göre kabaca doğrusal):

| Girdi | 1 iş parçacığı | 4 iş parçacığı |
|---|---|---|
| 320×240 | 0.53 s | — |
| **480×360** | **1.28 s** | — |
| 640×480 | 2.26 s | 0.85 s |
| 1920×1080 | — | 5.91 s |

Varsayılan 480×360, 2 saniyelik yayın periyoduna rahat sığar. Tepe bellek ~1 GB.

Çıkarım `asyncio.to_thread` ile ayrı iş parçacığında koşar: doğrudan çağrılsaydı
event loop bloklanır, MQTT keepalive kaçar, broker istemciyi düşürür ve vasiyet
tetiklenip backend cihazı **tam çalışırken** çevrimdışı işaretlerdi.

## Testler

```bash
cd edge
uv run pytest                    # birim testler (torch gerekmez)
uv run pytest -m entegrasyon     # gerçek ağırlıkla sayım doğruluğu
```

Entegrasyon testi iki sessiz hatayı kilitler: yanlış normalizasyon şeması
(gürültüden 55.9 kişi halüsinasyonu) ve yanlış ağırlık (Part A düz karede 7.33
hayalet kişi). İkisi de kod çalışıyormuş gibi görünüp sayıyı bozar.
