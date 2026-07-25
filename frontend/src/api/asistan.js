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
