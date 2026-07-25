import { apiPost, ASISTAN_TABANI } from './client'

// POST /chat -> asistanın Türkçe cevabı + hangi tool'ları çağırdığı.
// Asistan lokal LLM ile çalıştığı için cevap birkaç saniye sürebilir.
// `model` verilmezse servis kendi varsayılanını (qwen3.5:0.8b) kullanır.
export async function asistanaSor(mesaj, model) {
  const yanit = await apiPost('/chat', { mesaj, model }, ASISTAN_TABANI)
  return {
    cevap: yanit.cevap,
    aracCagrilari: yanit.arac_cagrilari ?? [],
    turSayisi: yanit.tur_sayisi ?? 0,
    model: yanit.model ?? '',
  }
}

// POST /chat/akis -> ajanın her adımı SSE olarak akar.
// EventSource kullanılmıyor: GET zorunlu kılar (soru sunucu log'una düşerdi) ve
// kopan isteği kendiliğinden yeniden başlatır — modeli ikinci kez koştururdu.
// `onOlay(tip, veri)` her adımda çağrılır; fonksiyon nihai cevabı döndürür.
export async function asistanaSorAkisli(mesaj, model, onOlay) {
  const yanit = await fetch(`${ASISTAN_TABANI}/chat/akis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ mesaj, model }),
  })
  if (!yanit.ok) throw new Error(`Akış başlatılamadı: ${yanit.status}`)

  const okuyucu = yanit.body.getReader()
  const cozucu = new TextDecoder()
  let tampon = ''
  let sonuc = null

  while (true) {
    const { done, value } = await okuyucu.read()
    if (done) break
    tampon += cozucu.decode(value, { stream: true })

    // SSE çerçeveleri boş satırla ayrılır; yarım çerçeve tamponda bekler.
    const cerceveler = tampon.split('\n\n')
    tampon = cerceveler.pop() ?? ''
    for (const cerceve of cerceveler) {
      const olay = _cerceveyiCoz(cerceve)
      if (!olay) continue
      if (olay.tip === 'bitti') sonuc = _cevabaCevir(olay.veri)
      else if (olay.tip === 'hata') throw new Error(olay.veri.mesaj ?? 'Akış hatası')
      else onOlay?.(olay.tip, olay.veri)
    }
  }

  if (!sonuc) throw new Error('Akış cevap üretmeden bitti.')
  return sonuc
}

function _cerceveyiCoz(cerceve) {
  let tip = null
  let ham = null
  for (const satir of cerceve.split('\n')) {
    if (satir.startsWith('event: ')) tip = satir.slice(7)
    else if (satir.startsWith('data: ')) ham = satir.slice(6)
  }
  if (!tip || ham === null) return null
  try {
    return { tip, veri: JSON.parse(ham) }
  } catch {
    return null // bozuk çerçeve akışı durdurmamalı
  }
}

function _cevabaCevir(veri) {
  return {
    cevap: veri.cevap,
    aracCagrilari: veri.arac_cagrilari ?? [],
    turSayisi: veri.tur_sayisi ?? 0,
    model: veri.model ?? '',
  }
}

// Seçilebilir modeller ve her birinin indirilmiş olup olmadığı.
export async function modelleriGetir() {
  const yanit = await fetch(`${ASISTAN_TABANI}/modeller`, {
    headers: { Accept: 'application/json' },
  })
  if (!yanit.ok) throw new Error(`Model listesi alınamadı: ${yanit.status}`)
  return yanit.json()
}

// Modeli Ollama'ya çeker. GB'larca sürebilir; çağıran beklemeyi göstermeli.
export async function modeliIndir(model) {
  return apiPost('/modeller/indir', { model }, ASISTAN_TABANI)
}
