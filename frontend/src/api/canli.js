import { API_TABANI } from './client'

// WS adresi HTTP tabanından türetilir: http->ws, https->wss. Ayrı bir derleme
// değişkeni gerekmez, adres değişince tek yerden takip eder.
export const WS_TABANI = API_TABANI.replace(/^http/, 'ws')

export const CANLI_YOLU = '/ws/canli'

// Backend yalnız değişiklikleri (delta) yayınlar; mesaj tipleri backend'deki
// ws_yayin.py ile birebir aynıdır.
export const MESAJ_ARAC_GUNCELLEME = 'arac_guncelleme'
export const MESAJ_CIHAZ_DURUM = 'cihaz_durum'

// Kopan bağlantı üstel olarak seyrelen aralıklarla denenir: broker/backend uzun
// süre kapalıysa tarayıcı boşuna istek yağdırmasın.
export const ILK_BEKLEME_MS = 1000
export const AZAMI_BEKLEME_MS = 30000

export function sonrakiBekleme(mevcut) {
  return Math.min(mevcut * 2, AZAMI_BEKLEME_MS)
}

// WebSocket kurulumunu tek yerde tutar; bileşenler ham soket API'siyle uğraşmaz.
export function canliyaBaglan({ onMesaj, onAcik, onKapali }) {
  const soket = new WebSocket(`${WS_TABANI}${CANLI_YOLU}`)

  soket.onopen = () => onAcik && onAcik()
  soket.onclose = () => onKapali && onKapali()
  // Hata sonrası her zaman close tetiklenir; yeniden bağlanma orada yönetilir.
  soket.onerror = () => soket.close()
  soket.onmessage = (olay) => {
    try {
      onMesaj(JSON.parse(olay.data))
    } catch {
      // Bozuk çerçeve akışı durdurmamalı; bir sonraki ölçüm zaten tazeleyecek.
    }
  }

  return soket
}
