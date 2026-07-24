import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet'
import { hatGuzergahiniGetir } from '../api/guzergahlar'

// Bir hattın sıralı durak akışını ve güzergah çizgisini gösteren modal.
export default function HatDetayModal({ hat, onClose }) {
  const [guzergah, setGuzergah] = useState(null)
  const [asama, setAsama] = useState('yukleniyor') // 'yukleniyor' | 'hazir' | 'hata'

  useEffect(() => {
    let iptal = false
    setAsama('yukleniyor')
    hatGuzergahiniGetir(hat.hat_id)
      .then((veri) => { if (!iptal) { setGuzergah(veri); setAsama('hazir') } })
      .catch(() => { if (!iptal) { setAsama('hata') } })
    return () => { iptal = true }
  }, [hat.hat_id])

  const merkez = guzergah?.duraklar?.length > 0
    ? [guzergah.duraklar[0].enlem, guzergah.duraklar[0].boylam]
    : [41.023, 29.015]

  return (
    <div style={s.overlay} onClick={onClose}>
      <div style={s.panel} onClick={(e) => e.stopPropagation()}>
        <div style={s.header}>
          <div>
            <div style={s.hatKodu}>{hat.code}</div>
            <div style={s.hatAdi}>{hat.route}</div>
          </div>
          <button style={s.closeBtn} onClick={onClose}>✕</button>
        </div>

        {asama === 'yukleniyor' && <div style={s.durumKutu}>Güzergah yükleniyor…</div>}
        {asama === 'hata' && <div style={s.durumKutu}>Güzergah bilgisi alınamadı.</div>}

        {asama === 'hazir' && guzergah && (
          <div style={s.body}>
            <div style={s.mapWrap}>
              <MapContainer center={merkez} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  attribution='&copy; OpenStreetMap &copy; CARTO'
                  url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                />
                {guzergah.koordinatlar.length > 0 && (
                  <Polyline positions={guzergah.koordinatlar} color="#111827" weight={4} opacity={0.8} />
                )}
                {guzergah.duraklar.map((d) => (
                  <Marker key={d.id} position={[d.enlem, d.boylam]}>
                    <Popup>{d.ad}</Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>

            <div style={s.durakListesi}>
              <div style={s.durakListesiBaslik}>DURAK AKIŞI ({guzergah.duraklar.length})</div>
              <div style={s.durakItems}>
                {guzergah.duraklar.map((d, i) => (
                  <div key={d.id} style={s.durakItem}>
                    <div style={s.durakSira}>{i + 1}</div>
                    <div style={s.durakAd}>{d.ad}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const s = {
  overlay: { position: 'fixed', inset: 0, background: 'rgba(17,24,39,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  panel: { background: '#fff', borderRadius: '16px', width: '860px', maxWidth: '92vw', maxHeight: '86vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '20px 24px', borderBottom: '1px solid #e5e7eb' },
  hatKodu: { fontSize: '22px', fontWeight: '700', color: '#111827' },
  hatAdi: { fontSize: '14px', color: '#6b7280', marginTop: '2px' },
  closeBtn: { border: 'none', background: '#f3f4f6', width: '32px', height: '32px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', color: '#6b7280' },
  durumKutu: { padding: '60px', textAlign: 'center', color: '#6b7280', fontSize: '14px' },
  body: { display: 'flex', flex: 1, overflow: 'hidden' },
  mapWrap: { flex: '1.4', minWidth: 0 },
  durakListesi: { flex: '1', minWidth: '260px', borderLeft: '1px solid #e5e7eb', padding: '18px', overflow: 'auto' },
  durakListesiBaslik: { fontSize: '11px', fontWeight: '600', color: '#9ca3af', letterSpacing: '0.05em', marginBottom: '12px' },
  durakItems: { display: 'flex', flexDirection: 'column', gap: '2px' },
  durakItem: { display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 0' },
  durakSira: { width: '22px', height: '22px', borderRadius: '50%', background: '#f3f4f6', color: '#374151', fontSize: '11px', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  durakAd: { fontSize: '13px', color: '#111827', fontWeight: '500' },
}
