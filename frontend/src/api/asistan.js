import { apiPost, ASISTAN_TABANI } from './client'

// POST /chat -> asistanın Türkçe cevabı + hangi tool'ları çağırdığı.
// Asistan lokal LLM ile çalıştığı için cevap birkaç saniye sürebilir.
export async function asistanaSor(mesaj) {
  const yanit = await apiPost('/chat', { mesaj }, ASISTAN_TABANI)
  return {
    cevap: yanit.cevap,
    aracCagrilari: yanit.arac_cagrilari ?? [],
  }
}
