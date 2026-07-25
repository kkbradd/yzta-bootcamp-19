import { useEffect, useRef, useState } from 'react'
import { asistanaSor, modelleriGetir, modeliIndir } from '../api/asistan'
import { ASISTAN_TABANI } from '../api/client'

// Ekip içi deneme ekranı: panelden bağımsız, oturum gerektirmez. Widget'tan farkı,
// her cevabın hangi tool'ları çağırdığını ve ne kadar sürdüğünü göstermesidir —
// tool çağırma davranışı qwen3.5:0.8b'de prompt'a duyarlı, gözle takip edilebilmeli.

const ORNEK_SORULAR = [
  'Şu an en yoğun hat hangisi?',
  '15A hattının anlık durumu nedir?',
  '15U hattı son 3 saatte nasıl seyretti?',
  'Yağmurlu havada yoğun saatte doluluk ne olur?',
  'Karlı havada sakin saatte ne bekleniyor?',
]

const ARAC_ETIKETLERI = {
  hat_yogunluklari: 'Tüm hatların anlık doluluğu',
  hat_anlik_durum: 'Bir hattaki araçların durumu',
  hat_trend: 'Hattın saatlik seyri',
  yogunluk_tahmini: 'Hava + saat ile doluluk tahmini (demo model)',
}

function saniyeMetni(milisaniye) {
  return `${(milisaniye / 1000).toFixed(1)} sn`
}

function AracRozetleri({ cagrilar }) {
  if (cagrilar.length === 0) {
    return <span style={stiller.aracYok}>tool çağrılmadı</span>
  }
  return (
    <>
      {cagrilar.map((arac, sira) => (
        <span key={`${arac}-${sira}`} style={stiller.aracRozeti} title={ARAC_ETIKETLERI[arac] ?? arac}>
          {arac}
        </span>
      ))}
    </>
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
              <button
                type="button"
                style={stiller.indirDugmesi}
                disabled={kilitli || buIndiriliyor}
                onClick={() => onIndir(model.ad)}
              >
                {buIndiriliyor ? 'indiriliyor…' : 'indir'}
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}

function CevapKarti({ kayit }) {
  return (
    <div style={stiller.kart}>
      <div style={stiller.soru}>{kayit.soru}</div>
      <div style={kayit.hataliMi ? stiller.hataMetni : stiller.cevap}>{kayit.cevap}</div>
      <div style={stiller.ustBilgi}>
        <AracRozetleri cagrilar={kayit.aracCagrilari} />
        <span style={stiller.olcum}>
          {kayit.model && `${kayit.model} · `}
          {kayit.turSayisi} tur · {saniyeMetni(kayit.sureMs)}
        </span>
      </div>
    </div>
  )
}

export default function AsistanTestPage() {
  const [girdi, setGirdi] = useState('')
  const [kayitlar, setKayitlar] = useState([])
  const [bekliyor, setBekliyor] = useState(false)
  const [modeller, setModeller] = useState([])
  const [seciliModel, setSeciliModel] = useState('')
  const [indirilen, setIndirilen] = useState('')
  const [modelHatasi, setModelHatasi] = useState('')
  const sonRef = useRef(null)

  useEffect(() => {
    sonRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [kayitlar, bekliyor])

  useEffect(() => {
    let iptal = false
    modelleriGetir()
      .then((liste) => {
        if (iptal) return
        setModeller(liste)
        // Varsayılan model konteyner açılışında çekilir; seçili olarak onunla başla.
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
      setModeller((onceki) =>
        onceki.map((m) => (m.ad === model ? { ...m, indirildi_mi: true } : m)),
      )
      setSeciliModel(model)
    } catch (hata) {
      setModelHatasi(`${model} indirilemedi: ${hata.message}`)
    } finally {
      setIndirilen('')
    }
  }

  async function sor(soru) {
    if (!soru || bekliyor) return
    setBekliyor(true)
    setGirdi('')
    const baslangic = performance.now()
    try {
      const yanit = await asistanaSor(soru, seciliModel || undefined)
      setKayitlar((onceki) => [
        ...onceki,
        { ...yanit, soru, sureMs: performance.now() - baslangic, hataliMi: false },
      ])
    } catch (hata) {
      setKayitlar((onceki) => [
        ...onceki,
        {
          soru,
          cevap: `Asistana ulaşılamadı (${ASISTAN_TABANI}): ${hata.message}`,
          aracCagrilari: [],
          turSayisi: 0,
          sureMs: performance.now() - baslangic,
          hataliMi: true,
        },
      ])
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <div style={stiller.kok}>
      <header style={stiller.baslikAlani}>
        <h1 style={stiller.baslik}>YOTAY Asistan — Deneme Ekranı</h1>
        <p style={stiller.altBaslik}>
          Ekip içi test alanı. Her cevabın altında hangi tool'ların çağrıldığı ve süresi görünür.
        </p>
        <code style={stiller.adres}>{ASISTAN_TABANI}</code>
      </header>

      <section style={stiller.ornekAlani}>
        <div style={stiller.ornekBaslik}>Model</div>
        <ModelSecici
          modeller={modeller}
          secili={seciliModel}
          onSec={setSeciliModel}
          onIndir={indir}
          indirilen={indirilen}
          kilitli={bekliyor || Boolean(indirilen)}
        />
        {indirilen && (
          <div style={stiller.modelUyarisi}>
            {indirilen} indiriliyor — birkaç dakika sürebilir, sayfayı kapatmayın.
          </div>
        )}
        {modelHatasi && <div style={stiller.modelHatasi}>{modelHatasi}</div>}
      </section>

      <section style={stiller.ornekAlani}>
        <div style={stiller.ornekBaslik}>Örnek sorular</div>
        <div style={stiller.ornekListesi}>
          {ORNEK_SORULAR.map((ornek) => (
            <button
              key={ornek}
              type="button"
              style={stiller.ornekDugmesi}
              disabled={bekliyor}
              onClick={() => sor(ornek)}
            >
              {ornek}
            </button>
          ))}
        </div>
      </section>

      <section style={stiller.akis}>
        {kayitlar.length === 0 && !bekliyor && (
          <div style={stiller.bosDurum}>Bir soru sorun ya da yukarıdan örnek seçin.</div>
        )}
        {kayitlar.map((kayit, sira) => (
          <CevapKarti key={`${kayit.soru}-${sira}`} kayit={kayit} />
        ))}
        {bekliyor && <div style={stiller.bekleme}>Asistan düşünüyor… (lokal model, birkaç saniye sürebilir)</div>}
        <div ref={sonRef} />
      </section>

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

const stiller = {
  kok: {
    minHeight: '100vh', background: '#f9fafb', padding: '32px 20px',
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  baslikAlani: { width: '100%', maxWidth: '760px' },
  baslik: { fontSize: '22px', fontWeight: '700', color: '#111827', margin: 0 },
  altBaslik: { fontSize: '13px', color: '#6b7280', margin: '6px 0 0' },
  adres: {
    fontSize: '11px', color: '#6b7280', background: '#f3f4f6',
    padding: '2px 8px', borderRadius: '6px', display: 'inline-block', marginTop: '8px',
  },
  ornekAlani: { width: '100%', maxWidth: '760px' },
  ornekBaslik: { fontSize: '12px', fontWeight: '600', color: '#6b7280', marginBottom: '8px' },
  ornekListesi: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  modelListesi: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  modelKarti: {
    display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 10px',
    border: '1px solid #e5e7eb', borderRadius: '10px', background: '#ffffff',
  },
  modelKartiSecili: { borderColor: '#111827', boxShadow: '0 0 0 1px #111827' },
  modelSecDugmesi: {
    display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '1px',
    border: 'none', background: 'transparent', cursor: 'pointer', padding: 0, textAlign: 'left',
  },
  modelEtiketi: { fontSize: '12px', fontWeight: '600', color: '#111827' },
  modelBoyutu: { fontSize: '10px', color: '#9ca3af' },
  modelHazir: { fontSize: '10px', color: '#059669', fontWeight: '600' },
  indirDugmesi: {
    fontSize: '11px', fontWeight: '600', padding: '4px 10px', borderRadius: '999px',
    border: '1px solid #d1d5db', background: '#f9fafb', color: '#374151', cursor: 'pointer',
  },
  modelUyarisi: { fontSize: '11px', color: '#92400e', marginTop: '8px' },
  modelHatasi: { fontSize: '11px', color: '#b91c1c', marginTop: '8px' },
  ornekDugmesi: {
    fontSize: '12px', padding: '6px 12px', borderRadius: '999px',
    border: '1px solid #e5e7eb', background: '#ffffff', color: '#374151', cursor: 'pointer',
  },
  akis: {
    width: '100%', maxWidth: '760px', display: 'flex', flexDirection: 'column', gap: '12px',
  },
  bosDurum: {
    fontSize: '13px', color: '#9ca3af', textAlign: 'center', padding: '32px 0',
  },
  kart: {
    background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '16px',
  },
  soru: { fontSize: '13px', fontWeight: '600', color: '#111827', marginBottom: '8px' },
  cevap: { fontSize: '14px', color: '#374151', lineHeight: 1.6, whiteSpace: 'pre-wrap' },
  hataMetni: { fontSize: '13px', color: '#b91c1c', lineHeight: 1.6 },
  ustBilgi: {
    display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px',
    marginTop: '12px', paddingTop: '10px', borderTop: '1px solid #f3f4f6',
  },
  aracRozeti: {
    fontSize: '11px', fontWeight: '600', color: '#3730a3', background: '#eef2ff',
    padding: '3px 8px', borderRadius: '999px',
  },
  aracYok: { fontSize: '11px', color: '#9ca3af', fontStyle: 'italic' },
  olcum: { fontSize: '11px', color: '#9ca3af', marginLeft: 'auto' },
  bekleme: { fontSize: '13px', color: '#6b7280', textAlign: 'center', padding: '12px' },
  form: { width: '100%', maxWidth: '760px', display: 'flex', gap: '8px' },
  girdi: {
    flex: 1, padding: '11px 14px', fontSize: '14px', borderRadius: '10px',
    border: '1px solid #e5e7eb', outline: 'none',
  },
  gonderDugmesi: {
    padding: '11px 20px', background: '#111827', color: '#ffffff', border: 'none',
    borderRadius: '10px', fontSize: '14px', fontWeight: '600', cursor: 'pointer',
  },
}
