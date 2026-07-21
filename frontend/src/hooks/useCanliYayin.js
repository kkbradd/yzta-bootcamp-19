import { useEffect, useState } from 'react'
import { API_TABANI } from '../api/client'

// /ws/canli WebSocket'ine bağlanır; arac_konum ve arac_guncelleme mesajlarını
// arac_id anahtarlı state'lere toplar. Bağlantı koparsa otomatik yeniden dener.
export function useCanliYayin() {
  const [aracKonumlari, setAracKonumlari] = useState({}) // { [arac_id]: {enlem, boylam, hat_id} }
  const [aracDurumlari, setAracDurumlari] = useState({}) // { [arac_id]: {doluluk_orani, seviye, ...} }

  useEffect(() => {
    let ws
    let kapatildi = false
    let yeniden_baglanma_zamanlayici

    const baglan = () => {
      const wsUrl = API_TABANI.replace(/^http/, 'ws') + '/ws/canli'
      ws = new WebSocket(wsUrl)

      ws.onmessage = (olay) => {
        const mesaj = JSON.parse(olay.data)
        if (mesaj.tip === 'arac_konum') {
          setAracKonumlari((onceki) => ({ ...onceki, [mesaj.arac_id]: mesaj }))
        } else if (mesaj.tip === 'arac_guncelleme') {
          setAracDurumlari((onceki) => ({ ...onceki, [mesaj.arac_id]: mesaj }))
        }
      }

      ws.onclose = () => {
        if (!kapatildi) {
          yeniden_baglanma_zamanlayici = setTimeout(baglan, 3000)
        }
      }
    }

    baglan()

    return () => {
      kapatildi = true
      clearTimeout(yeniden_baglanma_zamanlayici)
      ws?.close()
    }
  }, [])

  return { aracKonumlari, aracDurumlari }
}
