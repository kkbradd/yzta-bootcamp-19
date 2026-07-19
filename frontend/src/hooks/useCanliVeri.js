import { useEffect, useRef, useState } from 'react'
import {
  canliyaBaglan,
  ILK_BEKLEME_MS,
  MESAJ_ARAC_GUNCELLEME,
  MESAJ_CIHAZ_DURUM,
  sonrakiBekleme,
} from '../api/canli'

// Canlı ölçümleri WebSocket'ten dinler; kopan bağlantıyı kendisi toparlar.
// Araçlar arac_id, cihazlar cihaz_id anahtarıyla saklanır (backend delta yolluyor).
export function useCanliVeri() {
  const [araclar, setAraclar] = useState({})
  const [cihazlar, setCihazlar] = useState({})
  const [bagli, setBagli] = useState(false)
  const soketRef = useRef(null)
  const zamanlayiciRef = useRef(null)
  const beklemeRef = useRef(ILK_BEKLEME_MS)

  useEffect(() => {
    // Bileşen söküldükten sonra gecikmeli bağlanma çalışmasın: soket sızardı.
    let sokuldu = false

    function mesajIsle(mesaj) {
      if (mesaj.tip === MESAJ_ARAC_GUNCELLEME) {
        setAraclar((oncekiler) => ({ ...oncekiler, [mesaj.arac_id]: mesaj }))
        return
      }
      if (mesaj.tip === MESAJ_CIHAZ_DURUM) {
        setCihazlar((oncekiler) => ({ ...oncekiler, [mesaj.cihaz_id]: mesaj }))
      }
    }

    function baglan() {
      if (sokuldu) return
      soketRef.current = canliyaBaglan({
        onMesaj: mesajIsle,
        onAcik: () => {
          setBagli(true)
          beklemeRef.current = ILK_BEKLEME_MS // başarılı bağlantı sayacı sıfırlar
        },
        onKapali: () => {
          setBagli(false)
          if (sokuldu) return
          zamanlayiciRef.current = setTimeout(baglan, beklemeRef.current)
          beklemeRef.current = sonrakiBekleme(beklemeRef.current)
        },
      })
    }

    baglan()

    return () => {
      sokuldu = true
      // Hem soket hem bekleyen zamanlayıcı temizlenmeli; zamanlayıcı unutulursa
      // söküm sonrası tetiklenip öksüz bir soket açar.
      clearTimeout(zamanlayiciRef.current)
      soketRef.current?.close()
    }
  }, [])

  return { araclar, cihazlar, bagli }
}
