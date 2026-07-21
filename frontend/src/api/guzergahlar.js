import { apiGet } from './client'

// GET /api/hatlar/{hatId}/guzergah -> sıralı duraklar + OSRM polyline koordinatları.
export async function hatGuzergahiniGetir(hatId) {
  const veri = await apiGet(`/api/hatlar/${hatId}/guzergah`)
  return {
    duraklar: veri.duraklar,
    koordinatlar: veri.koordinatlar, // [[enlem, boylam], ...]
    mesafeMetre: veri.mesafe_metre,
    sureSaniye: veri.sure_saniye,
  }
}
