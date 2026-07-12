# MQTT Sözleşmesi

Broker: `mosquitto` (compose) / `localhost:1883` (yerel), `allow_anonymous true` (yalnız geliştirme; TLS/ACL yok). Backend sadece **dinler**, publish etmez.

## Topic desenleri (koda sabit)

- `filo/{cihaz_id}/yogunluk`
- `filo/{cihaz_id}/durum`

Her ikisi de **QoS 1** ile dinlenir. Topic `/` ile üç parçaya bölünmezse veya üçüncü parça `yogunluk`/`durum` değilse mesaj düşürülür.

## Yoğunluk payload'ı (3 alan)

```jsonc
{
  "sira_no": 1024,        // int (alt sınır yok, negatif kabul)
  "kisi_sayisi": 42,      // int, ge=0 (negatif -> bozuk mesaj, düşürülür)
  "timestamp": "2026-07-10T12:00:00Z"  // datetime — çekim anı (ISO 8601; Z veya +00:00 kabul edilir)
}
```

> Dikkat: alan adı **`timestamp`** (İngilizce). `olcum_zamani` / `zaman` değil. Yanlış anahtar → ValidationError → mesaj sessizce düşer.

## Durum payload'ı (2 alan)

```jsonc
{
  "cevrimici": true,               // bool, zorunlu
  "yazilim_surumu": "1.0.0"        // str | null, opsiyonel
}
```

## Retained / LWT

Backend will/retain **üretmez**; sadece gelen mesajın `retain` bayrağını okur. Retained durum mesajı gelirse `son_gorulme=None` geçirilir → `AnlikDurumPort` mevcut `son_gorulme`'yi korur (retained tekrar oynatma "şimdi görüldü" saymaz). LWT'yi kurmak cihaz/simulator veya broker'ın işidir. Kayıt/atama doğrulaması **sadece yoğunluk yolunda** vardır; durum mesajı doğrudan yazılır.

## Dedup

Uygulama katmanında "gördüm mü" kontrolü yok. Her mesaj insert'lenir; benzersizlik DB'de `UNIQUE(cihaz_id, sira_no)` + `ON CONFLICT DO NOTHING` ile korunur. Mükerrerse hiçbir yan etki üretilmez (yazma/yayın yok). Anahtar **çift**tir: `(cihaz_id, sira_no)` — farklı cihazlar aynı `sira_no`'yu kullanabilir; çakışma sadece aynı cihaz+aynı sıra_no'da olur. `timestamp` dedup'a dahil değil.

## Hata politikası

İki ayrı sınır:
1. **Parse/doğrulama hatası** → uyarı loglanır, mesaj düşürülür, akış durmaz.
2. **İşleme hatası** → `logger.exception`, akış yine durmaz.

Bağlantı koparsa 3 sn bekleyip yeniden bağlanır.

## Referans yayıncı

`backend/simulator/simulator.py`, N sahte cihazla gerçekçi kişi sayıları üretip MQTT'ye yayınlayan bir betiktir; kendi yayıncını yazarken doğrudan referans alınabilir. Tünel modu (`--tunel`) 4G kesintisi simüle eder: cihaz süre boyunca yayın yapmaz, ölçümleri çekim damgalarıyla biriktirir, süre dolunca hepsini artan `sira_no` ile tek seferde boşaltır.

Kesin kaynak referansı için bkz. `backend/README.md`.
