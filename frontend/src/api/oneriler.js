import { apiGet, apiPost } from './client'

const GUN_ADLARI = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']

// Karşılaştırma ortalamasına göre öncelik: sapma ne kadar büyükse o kadar acil.
function oncelikBelirle(oneri) {
  const fark = oneri.karsilastirma_ortalama_doluluk == null
    ? 0
    : oneri.ortalama_doluluk - oneri.karsilastirma_ortalama_doluluk
  if (fark >= 0.3) return { priority: 'High Priority', color: '#ef4444', bg: '#fef2f2' }
  if (fark >= 0.15) return { priority: 'Medium Priority', color: '#f59e0b', bg: '#fffbeb' }
  return { priority: 'Low Priority', color: '#3b82f6', bg: '#eff6ff' }
}

// GET /api/oneriler -> UI kart şekli.
export async function onerileriGetir(limit = 10) {
  const oneriler = await apiGet(`/api/oneriler?limit=${limit}`)
  return oneriler.map((o) => ({
    id: o.id,
    hatId: o.hat_id,
    gun: GUN_ADLARI[o.gun_no] ?? '',
    text: o.oneri_metni,
    gerekce: o.gerekce,
    ...oncelikBelirle(o),
  }))
}

// POST /api/oneriler/uret -> zamanlamayı beklemeden motoru tetikler.
export async function oneriUret() {
  return apiPost('/api/oneriler/uret', {})
}

function uyariRengiBelirle(uyari) {
  if (uyari.ortalama_doluluk >= 0.85) return '#ef4444'
  return '#f59e0b'
}

// GET /api/uyarilar -> UI kart şekli.
export async function uyarilariGetir(limit = 10) {
  const uyarilar = await apiGet(`/api/uyarilar?limit=${limit}`)
  return uyarilar.map((u) => ({
    id: u.id,
    hatId: u.hat_id,
    title: `Hat ${u.hat_id}`,
    desc: u.uyari_metni,
    time: new Date(u.olusturulma_zamani).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
    color: uyariRengiBelirle(u),
  }))
}
