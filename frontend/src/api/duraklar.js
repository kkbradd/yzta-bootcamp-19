import { apiGet } from './client'

// GET /api/duraklar -> harita ve Duraklar sayfası için koordinatlı durak listesi.
export async function duraklariGetir() {
  const duraklar = await apiGet('/api/duraklar')
  return duraklar.map((d) => ({
    id: d.id,
    ad: d.ad,
    enlem: d.enlem,
    boylam: d.boylam,
    hatKodlari: d.hat_kodlari ?? [],
  }))
}
