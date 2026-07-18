import { useEffect, useRef, useState } from 'react'
import { asistanaSor } from '../api/asistan'
import { ASISTAN_TABANI } from '../api/client'

const KARSILAMA = {
  kim: 'asistan',
  metin: 'Merhaba! Hat yoğunlukları hakkında soru sorabilirsiniz. Örnek: "Şu an en yoğun hat hangisi?"',
}

// Asistan lokal modelle çalışır; cevap gecikmesi normaldir (bkz. asistan/README.md).
const YAZIYOR = 'Düşünüyor…'

export default function AsistanWidget() {
  const [acik, setAcik] = useState(false)
  const [mesajlar, setMesajlar] = useState([KARSILAMA])
  const [girdi, setGirdi] = useState('')
  const [bekliyor, setBekliyor] = useState(false)
  const sonRef = useRef(null)

  useEffect(() => {
    sonRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mesajlar, bekliyor])

  async function gonder(olay) {
    olay.preventDefault()
    const soru = girdi.trim()
    if (!soru || bekliyor) return

    setMesajlar((onceki) => [...onceki, { kim: 'kullanici', metin: soru }])
    setGirdi('')
    setBekliyor(true)
    try {
      const { cevap, aracCagrilari } = await asistanaSor(soru)
      setMesajlar((onceki) => [...onceki, { kim: 'asistan', metin: cevap, araclar: aracCagrilari }])
    } catch {
      setMesajlar((onceki) => [
        ...onceki,
        { kim: 'hata', metin: `Asistana ulaşılamadı (${ASISTAN_TABANI}). Servis ayakta mı?` },
      ])
    } finally {
      setBekliyor(false)
    }
  }

  if (!acik) {
    return (
      <button style={s.fab} onClick={() => setAcik(true)} title="YOTAY Asistan">
        💬
      </button>
    )
  }

  return (
    <div style={s.panel}>
      <div style={s.baslik}>
        <div style={s.baslikSol}>
          <span style={s.nokta} />
          <span style={s.baslikMetin}>YOTAY Asistan</span>
        </div>
        <button style={s.kapat} onClick={() => setAcik(false)} title="Kapat">×</button>
      </div>

      <div style={s.akis}>
        {mesajlar.map((m, i) => (
          <div key={i} style={{ ...s.balon, ...BALON_STILI[m.kim] }}>
            {m.metin}
            {m.araclar?.length > 0 && <div style={s.araclar}>Kullanılan veri: {m.araclar.join(', ')}</div>}
          </div>
        ))}
        {bekliyor && <div style={{ ...s.balon, ...BALON_STILI.asistan, ...s.yaziyor }}>{YAZIYOR}</div>}
        <div ref={sonRef} />
      </div>

      <form style={s.form} onSubmit={gonder}>
        <input
          style={s.girdi}
          value={girdi}
          onChange={(e) => setGirdi(e.target.value)}
          placeholder="Bir soru yazın…"
          disabled={bekliyor}
        />
        <button style={{ ...s.gonder, ...(bekliyor ? s.gonderPasif : {}) }} disabled={bekliyor}>
          ↑
        </button>
      </form>
    </div>
  )
}

const BALON_STILI = {
  kullanici: { alignSelf: 'flex-end', background: '#111827', color: '#fff' },
  asistan: { alignSelf: 'flex-start', background: '#f3f4f6', color: '#111827' },
  hata: { alignSelf: 'flex-start', background: '#fffbeb', color: '#92400e', border: '1px solid #fde68a' },
}

const s = {
  fab: { position: 'fixed', right: '24px', bottom: '24px', width: '52px', height: '52px', borderRadius: '50%', background: '#111827', color: '#fff', border: 'none', fontSize: '22px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' },
  panel: { position: 'fixed', right: '24px', bottom: '24px', width: '360px', height: '480px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '14px', boxShadow: '0 8px 24px rgba(0,0,0,0.12)', display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  baslik: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', borderBottom: '1px solid #e5e7eb', flexShrink: 0 },
  baslikSol: { display: 'flex', alignItems: 'center', gap: '8px' },
  baslikMetin: { fontSize: '14px', fontWeight: '600', color: '#111827' },
  nokta: { width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 0 2px #d1fae5' },
  kapat: { background: 'none', border: 'none', fontSize: '20px', color: '#9ca3af', cursor: 'pointer', lineHeight: 1 },
  akis: { flex: 1, overflowY: 'auto', padding: '14px', display: 'flex', flexDirection: 'column', gap: '10px' },
  balon: { maxWidth: '80%', padding: '9px 12px', borderRadius: '12px', fontSize: '13px', lineHeight: 1.5, whiteSpace: 'pre-wrap' },
  yaziyor: { color: '#9ca3af', fontStyle: 'italic' },
  araclar: { marginTop: '6px', fontSize: '10px', color: '#6b7280', letterSpacing: '0.03em' },
  form: { display: 'flex', gap: '8px', padding: '12px', borderTop: '1px solid #e5e7eb', flexShrink: 0 },
  girdi: { flex: 1, padding: '9px 12px', border: '1px solid #e5e7eb', borderRadius: '10px', fontSize: '13px', outline: 'none', color: '#111827', background: '#fff' },
  gonder: { width: '38px', border: 'none', borderRadius: '10px', background: '#111827', color: '#fff', fontSize: '15px', cursor: 'pointer' },
  gonderPasif: { background: '#9ca3af', cursor: 'default' },
}
