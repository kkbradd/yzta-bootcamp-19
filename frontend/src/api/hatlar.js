import { apiGet } from './client'

// Backend seviye (seyrek/orta/yogun) -> UI durumu (dusuk/orta/yuksek); veri yoksa 'veriyok'.
const SEVIYE_ESLEME = { seyrek: 'dusuk', orta: 'orta', yogun: 'yuksek' }

export function seviyeToDurum(seviye) {
  return SEVIYE_ESLEME[seviye] ?? 'veriyok'
}

// GET /api/hatlar -> UI kart şekli. duration/stops backend'de yok (sayfada '—').
export async function hatlariGetir() {
  const hatlar = await apiGet('/api/hatlar')
  return hatlar.map((h) => ({
    hat_id: h.hat_id,
    code: h.hat_no,
    route: h.ad,
    buses: h.arac_sayisi,
    durum: seviyeToDurum(h.seviye),
    ortalamaDoluluk: h.ortalama_doluluk,
  }))
}
