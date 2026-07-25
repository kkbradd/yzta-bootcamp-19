import { useEffect, useRef, useState } from 'react'
import { asistanaSorAkisli, modelleriGetir, modeliIndir } from '../api/asistan'
import { ASISTAN_TABANI } from '../api/client'

// Ekip içi deneme ekranı: panelden bağımsız, oturum gerektirmez.
// İki sekme — "Sohbet" normal chatbot görünümü, "EventBus" ajanın her adımını
// ham hâliyle gösterir. Tool çağırma davranışı küçük modelde prompt'a duyarlı,
// gözle takip edilebilmeli.

const ORNEK_SORULAR = [
  'Şu an en yoğun hat hangisi?',
  '15A hattının anlık durumu nedir?',
  '15U hattı son 3 saatte nasıl seyretti?',
  'Yağmurlu havada yoğun saatte doluluk ne olur?',
]

const ARAC_ETIKETLERI = {
  hat_yogunluklari: 'Tüm hatların anlık doluluğu',
  hat_anlik_durum: 'Bir hattaki araçların durumu',
  hat_trend: 'Hattın saatlik seyri',
  yogunluk_tahmini: 'Hava + saat ile doluluk tahmini (demo model)',
}

// Modelin gerçekte ürettiği tek markdown öğesi **kalın** (canlı çıktı analizi).
// Liste/başlık/tablo çıkmadığı için tam markdown kütüphanesi eklenmedi.
function KalinMetin({ metin }) {
  return (
    <>
      {metin.split(/(\*\*[^*]+\*\*)/g).map((parca, sira) =>
        parca.startsWith('**') && parca.endsWith('**') && parca.length > 4 ? (
          <strong key={sira}>{parca.slice(2, -2)}</strong>
        ) : (
          parca
        ),
      )}
    </>
  )
}

function Balon({ mesaj }) {
  const toolYok = mesaj.kim === 'asistan' && mesaj.aracCagrilari?.length === 0
  return (
    <div style={{ ...stiller.balon, ...BALON_STILI[mesaj.kim] }}>
      <KalinMetin metin={mesaj.metin} />
      {mesaj.aracCagrilari?.length > 0 && (
        <div style={stiller.balonAlt}>
          {mesaj.aracCagrilari.map((arac, sira) => (
            <span key={`${arac}-${sira}`} style={stiller.aracRozeti} title={ARAC_ETIKETLERI[arac] ?? arac}>
              {arac}
            </span>
          ))}
          {mesaj.sureMs != null && (
            <span style={stiller.olcum}>
              {mesaj.model && `${mesaj.model} · `}
              {(mesaj.sureMs / 1000).toFixed(1)} sn
            </span>
          )}
        </div>
      )}
      {toolYok && (
        <div style={stiller.uyariAlt}>araç kullanılmadı — cevap doğrulanmadı</div>
      )}
    </div>
  )
}

function OlaySatiri({ olay, baslangic }) {
  const gecen = ((olay.zaman * 1000 - baslangic) / 1000).toFixed(2)
  return (
    <div style={stiller.olaySatiri}>
      <span style={stiller.olayZaman}>+{gecen}s</span>
      <span style={{ ...stiller.olayTipi, ...(OLAY_RENGI[olay.tip] ?? {}) }}>{olay.tip}</span>
      <pre style={stiller.olayVeri}>{JSON.stringify(olay.veri, null, 1)}</pre>
    </div>
  )
}

function ModelSecici({ modeller, secili, onSec, onIndir, indirilen, kilitli }) {
  if (modeller.length === 0) {
    return <div style={stiller.modelUyarisi}>Model listesi alınamadı — asistan servisi ayakta mı?</div>
  }
  return (
    <div style={stiller.modelListesi}>
      {modeller.map((model) => {
        const seciliMi = model.ad === secili
        const buIndiriliyor = indirilen === model.ad
        return (
          <div key={model.ad} style={{ ...stiller.modelKarti, ...(seciliMi ? stiller.modelKartiSecili : {}) }}>
            <button
              type="button"
              style={stiller.modelSecDugmesi}
              disabled={kilitli || !model.indirildi_mi}
              onClick={() => onSec(model.ad)}
              title={model.indirildi_mi ? model.ad : 'Önce indirilmeli'}
            >
              <span style={stiller.modelEtiketi}>{model.etiket}</span>
              <span style={stiller.modelBoyutu}>{model.boyut}</span>
            </button>
            {model.indirildi_mi ? (
              <span style={stiller.modelHazir}>{seciliMi ? '● seçili' : 'hazır'}</span>
            ) : (
              <button type="button" style={stiller.indirDugmesi} disabled={kilitli || buIndiriliyor} onClick={() => onIndir(model.ad)}>
                {buIndiriliyor ? 'indiriliyor…' : 'indir'}
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default function AsistanTestPage() {
  const [sekme, setSekme] = useState('sohbet')
  const [girdi, setGirdi] = useState('')
  const [mesajlar, setMesajlar] = useState([])
  const [olaylar, setOlaylar] = useState([])
  const [bekliyor, setBekliyor] = useState(false)
  const [modeller, setModeller] = useState([])
  const [seciliModel, setSeciliModel] = useState('')
  const [indirilen, setIndirilen] = useState('')
  const [modelHatasi, setModelHatasi] = useState('')
  const sonRef = useRef(null)

  useEffect(() => {
    sonRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mesajlar, olaylar, bekliyor, sekme])

  useEffect(() => {
    let iptal = false
    modelleriGetir()
      .then((liste) => {
        if (iptal) return
        setModeller(liste)
        const varsayilan = liste.find((m) => m.varsayilan_mi) ?? liste.find((m) => m.indirildi_mi)
        setSeciliModel(varsayilan?.ad ?? '')
      })
      .catch((hata) => {
        if (!iptal) setModelHatasi(hata.message)
      })
    return () => {
      iptal = true
    }
  }, [])

  async function indir(model) {
    setIndirilen(model)
    setModelHatasi('')
    try {
      await modeliIndir(model)
      setModeller((onceki) => onceki.map((m) => (m.ad === model ? { ...m, indirildi_mi: true } : m)))
      setSeciliModel(model)
    } catch (hata) {
      setModelHatasi(`${model} indirilemedi: ${hata.message}`)
    } finally {
      setIndirilen('')
    }
  }

  async function sor(soru) {
    if (!soru || bekliyor) return
    // Soru ANINDA görünür: lokal model saniyelerce düşünürken ekran boş kalmamalı.
    setMesajlar((onceki) => [...onceki, { kim: 'kullanici', metin: soru }])
    setGirdi('')
    setBekliyor(true)
    const baslangic = performance.now()

    try {
      const yanit = await asistanaSorAkisli(soru, seciliModel || undefined, (tip, veri) =>
        setOlaylar((onceki) => [...onceki, { tip, ...veri }]),
      )
      setMesajlar((onceki) => [
        ...onceki,
        { kim: 'asistan', metin: yanit.cevap, ...yanit, sureMs: performance.now() - baslangic },
      ])
    } catch (hata) {
      setMesajlar((onceki) => [
        ...onceki,
        { kim: 'hata', metin: `Asistana ulaşılamadı (${ASISTAN_TABANI}): ${hata.message}` },
      ])
    } finally {
      setBekliyor(false)
    }
  }

  const ilkOlayZamani = olaylar.length > 0 ? olaylar[0].zaman * 1000 : 0

  return (
    <div style={stiller.kok}>
      <header style={stiller.baslikAlani}>
        <h1 style={stiller.baslik}>YOTAY Asistan — Deneme Ekranı</h1>
        <p style={stiller.altBaslik}>
          Ekip içi test alanı. Sohbet sekmesinde konuşun, EventBus sekmesinde ajanın her adımını izleyin.
        </p>
        <code style={stiller.adres}>{ASISTAN_TABANI}</code>
      </header>

      <div style={stiller.sekmeler}>
        <button
          type="button"
          style={{ ...stiller.sekme, ...(sekme === 'sohbet' ? stiller.sekmeAktif : {}) }}
          onClick={() => setSekme('sohbet')}
        >
          💬 Sohbet
        </button>
        <button
          type="button"
          style={{ ...stiller.sekme, ...(sekme === 'olaylar' ? stiller.sekmeAktif : {}) }}
          onClick={() => setSekme('olaylar')}
        >
          📡 EventBus {olaylar.length > 0 && <span style={stiller.sayac}>{olaylar.length}</span>}
        </button>
      </div>

      <section style={stiller.ustAlan}>
        <div style={stiller.ustBaslik}>Model</div>
        <ModelSecici
          modeller={modeller}
          secili={seciliModel}
          onSec={setSeciliModel}
          onIndir={indir}
          indirilen={indirilen}
          kilitli={bekliyor || Boolean(indirilen)}
        />
        {indirilen && <div style={stiller.modelUyarisi}>{indirilen} indiriliyor — birkaç dakika sürebilir.</div>}
        {modelHatasi && <div style={stiller.modelHatasi}>{modelHatasi}</div>}
      </section>

      {sekme === 'sohbet' ? (
        <>
          <section style={stiller.ustAlan}>
            <div style={stiller.ustBaslik}>Örnek sorular</div>
            <div style={stiller.ornekListesi}>
              {ORNEK_SORULAR.map((ornek) => (
                <button key={ornek} type="button" style={stiller.ornekDugmesi} disabled={bekliyor} onClick={() => sor(ornek)}>
                  {ornek}
                </button>
              ))}
            </div>
          </section>

          <section style={stiller.akis}>
            {mesajlar.length === 0 && !bekliyor && (
              <div style={stiller.bosDurum}>Bir soru sorun ya da yukarıdan örnek seçin.</div>
            )}
            {mesajlar.map((mesaj, sira) => (
              <Balon key={sira} mesaj={mesaj} />
            ))}
            {bekliyor && (
              <div style={{ ...stiller.balon, ...BALON_STILI.asistan, ...stiller.yaziyor }}>Düşünüyor…</div>
            )}
            <div ref={sonRef} />
          </section>
        </>
      ) : (
        <section style={stiller.olayAkisi}>
          {olaylar.length === 0 ? (
            <div style={stiller.bosDurum}>
              Henüz olay yok. Sohbet sekmesinden bir soru sorun; adımlar burada canlı akar.
            </div>
          ) : (
            olaylar.map((olay, sira) => <OlaySatiri key={sira} olay={olay} baslangic={ilkOlayZamani} />)
          )}
          <div ref={sonRef} />
        </section>
      )}

      <form
        style={stiller.form}
        onSubmit={(olay) => {
          olay.preventDefault()
          sor(girdi.trim())
        }}
      >
        <input
          style={stiller.girdi}
          value={girdi}
          onChange={(olay) => setGirdi(olay.target.value)}
          placeholder="Sorunuzu yazın…"
          disabled={bekliyor}
        />
        <button type="submit" style={stiller.gonderDugmesi} disabled={bekliyor || !girdi.trim()}>
          Gönder
        </button>
      </form>
    </div>
  )
}

const BALON_STILI = {
  kullanici: { alignSelf: 'flex-end', background: '#111827', color: '#ffffff' },
  asistan: { alignSelf: 'flex-start', background: '#f3f4f6', color: '#111827' },
  hata: { alignSelf: 'flex-start', background: '#fffbeb', color: '#92400e', border: '1px solid #fde68a' },
}

const OLAY_RENGI = {
  tool_call_start: { background: '#eef2ff', color: '#3730a3' },
  tool_call_end: { background: '#ecfdf5', color: '#065f46' },
  inference_start: { background: '#fef3c7', color: '#92400e' },
  inference_end: { background: '#fef3c7', color: '#92400e' },
}

const stiller = {
  kok: {
    minHeight: '100vh', background: '#f9fafb', padding: '32px 20px',
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  baslikAlani: { width: '100%', maxWidth: '760px' },
  baslik: { fontSize: '22px', fontWeight: '700', color: '#111827', margin: 0 },
  altBaslik: { fontSize: '13px', color: '#6b7280', margin: '6px 0 0' },
  adres: { fontSize: '11px', color: '#6b7280', background: '#f3f4f6', padding: '2px 8px', borderRadius: '6px', display: 'inline-block', marginTop: '8px' },
  sekmeler: { width: '100%', maxWidth: '760px', display: 'flex', gap: '8px' },
  sekme: {
    flex: 1, padding: '10px', fontSize: '14px', fontWeight: '600', cursor: 'pointer',
    border: '1px solid #e5e7eb', borderRadius: '10px', background: '#ffffff', color: '#6b7280',
  },
  sekmeAktif: { background: '#111827', color: '#ffffff', borderColor: '#111827' },
  sayac: { fontSize: '11px', opacity: 0.75, marginLeft: '4px' },
  ustAlan: { width: '100%', maxWidth: '760px' },
  ustBaslik: { fontSize: '12px', fontWeight: '600', color: '#6b7280', marginBottom: '8px' },
  ornekListesi: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  ornekDugmesi: { fontSize: '12px', padding: '6px 12px', borderRadius: '999px', border: '1px solid #e5e7eb', background: '#ffffff', color: '#374151', cursor: 'pointer' },
  modelListesi: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  modelKarti: { display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '10px', background: '#ffffff' },
  modelKartiSecili: { borderColor: '#111827', boxShadow: '0 0 0 1px #111827' },
  modelSecDugmesi: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '1px', border: 'none', background: 'transparent', cursor: 'pointer', padding: 0, textAlign: 'left' },
  modelEtiketi: { fontSize: '12px', fontWeight: '600', color: '#111827' },
  modelBoyutu: { fontSize: '10px', color: '#9ca3af' },
  modelHazir: { fontSize: '10px', color: '#059669', fontWeight: '600' },
  indirDugmesi: { fontSize: '11px', fontWeight: '600', padding: '4px 10px', borderRadius: '999px', border: '1px solid #d1d5db', background: '#f9fafb', color: '#374151', cursor: 'pointer' },
  modelUyarisi: { fontSize: '11px', color: '#92400e', marginTop: '8px' },
  modelHatasi: { fontSize: '11px', color: '#b91c1c', marginTop: '8px' },
  akis: { width: '100%', maxWidth: '760px', display: 'flex', flexDirection: 'column', gap: '10px', minHeight: '240px' },
  balon: { maxWidth: '78%', padding: '10px 14px', borderRadius: '14px', fontSize: '14px', lineHeight: 1.55, whiteSpace: 'pre-wrap' },
  balonAlt: { display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(0,0,0,0.07)' },
  aracRozeti: { fontSize: '11px', fontWeight: '600', color: '#3730a3', background: '#eef2ff', padding: '3px 8px', borderRadius: '999px' },
  olcum: { fontSize: '11px', color: '#9ca3af', marginLeft: 'auto' },
  uyariAlt: { fontSize: '11px', color: '#b45309', marginTop: '8px', fontStyle: 'italic' },
  yaziyor: { color: '#9ca3af', fontStyle: 'italic' },
  bosDurum: { fontSize: '13px', color: '#9ca3af', textAlign: 'center', padding: '32px 0' },
  olayAkisi: { width: '100%', maxWidth: '760px', display: 'flex', flexDirection: 'column', gap: '4px', minHeight: '240px', background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '12px' },
  olaySatiri: { display: 'flex', alignItems: 'flex-start', gap: '8px', padding: '6px 0', borderBottom: '1px solid #f3f4f6' },
  olayZaman: { fontSize: '11px', color: '#9ca3af', fontFamily: 'monospace', flexShrink: 0, width: '52px' },
  olayTipi: { fontSize: '11px', fontWeight: '600', padding: '2px 8px', borderRadius: '6px', flexShrink: 0, background: '#f3f4f6', color: '#6b7280' },
  olayVeri: { fontSize: '11px', color: '#374151', fontFamily: 'monospace', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word', flex: 1, maxHeight: '160px', overflowY: 'auto' },
  form: { width: '100%', maxWidth: '760px', display: 'flex', gap: '8px' },
  girdi: { flex: 1, padding: '11px 14px', fontSize: '14px', borderRadius: '10px', border: '1px solid #e5e7eb', outline: 'none' },
  gonderDugmesi: { padding: '11px 20px', background: '#111827', color: '#ffffff', border: 'none', borderRadius: '10px', fontSize: '14px', fontWeight: '600', cursor: 'pointer' },
}
