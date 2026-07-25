import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useCanliYayin } from '../hooks/useCanliYayin'
import { duraklariGetir } from '../api/duraklar'
import { hatlariGetir } from '../api/hatlar'
import { hatGuzergahiniGetir } from '../api/guzergahlar'

// Vite'da Leaflet'in varsayılan marker ikonları otomatik yüklenmez — CDN'den elle ayarlanır.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const USKUDAR_MERKEZ = [41.023, 29.015]

// Doluluk seviyesine göre otobüs ikonu rengi (StopsPage/LinesPage renk paletiyle tutarlı).
const DOLULUK_RENKLERI = { seyrek: '#22c55e', orta: '#f59e0b', yogun: '#ef4444' }

function aracIkonuOlustur(seviye) {
  const renk = DOLULUK_RENKLERI[seviye] ?? '#22c55e'
  return new L.DivIcon({
    className: 'arac-ikonu',
    html: `<div style="width:26px;height:26px;border-radius:50%;background:${renk};border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5">
        <path d="M4 16V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10"/>
        <path d="M4 16h16v2a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-1H7v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/>
        <line x1="4" y1="11" x2="20" y2="11"/>
        <circle cx="8" cy="19" r="1.3" fill="#fff"/>
        <circle cx="16" cy="19" r="1.3" fill="#fff"/>
      </svg>
    </div>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  })
}

const HAT_RENKLERI = ['#ef4444', '#f59e0b', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16']

// Duraklar, hat güzergahları ve canlı araç konumlarını gösteren paylaşılan harita.
// LiveMapPage ve DashboardPage aynı bileşeni birebir kullanır.
export default function CanliHarita({ style }) {
  const [duraklar, setDuraklar] = useState([])
  const [guzergahlar, setGuzergahlar] = useState([]) // [{ hatId, code, koordinatlar, renk }]
  const [hatKodlari, setHatKodlari] = useState({}) // { [hat_id]: '15A' }
  const { aracKonumlari, aracDurumlari } = useCanliYayin()

  useEffect(() => {
    duraklariGetir().then(setDuraklar).catch(() => setDuraklar([]))

    hatlariGetir()
      .then(async (hatlar) => {
        setHatKodlari(Object.fromEntries(hatlar.map((h) => [h.hat_id, h.code])))
        const sonuclar = await Promise.all(
          hatlar.map(async (hat, i) => {
            try {
              const guzergah = await hatGuzergahiniGetir(hat.hat_id)
              return {
                hatId: hat.hat_id,
                code: hat.code,
                koordinatlar: guzergah.koordinatlar,
                renk: HAT_RENKLERI[i % HAT_RENKLERI.length],
              }
            } catch {
              return null
            }
          })
        )
        setGuzergahlar(sonuclar.filter(Boolean))
      })
      .catch(() => setGuzergahlar([]))
  }, [])

  return (
    <MapContainer center={USKUDAR_MERKEZ} zoom={13} style={{ height: '100%', width: '100%', borderRadius: '8px', ...style }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />

      {guzergahlar.map((g) => (
        g.koordinatlar.length > 0 && (
          <Polyline key={g.hatId} positions={g.koordinatlar} color={g.renk} weight={4} opacity={0.7} />
        )
      ))}

      {duraklar.map((d) => (
        <Marker key={d.id} position={[d.enlem, d.boylam]}>
          <Popup>{d.ad}</Popup>
        </Marker>
      ))}

      {Object.entries(aracKonumlari).map(([aracId, konum]) => {
        const seviye = aracDurumlari[aracId]?.seviye ?? 'seyrek'
        return (
          <Marker key={aracId} position={[konum.enlem, konum.boylam]} icon={aracIkonuOlustur(seviye)}>
            <Popup>Araç #{aracId} — Hat {hatKodlari[konum.hat_id] ?? konum.hat_id}</Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}
