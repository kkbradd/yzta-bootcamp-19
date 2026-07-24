import { apiGet } from './client'

// UI aralık seçimi -> backend baslangic/bitis (ISO) + aralik (saat|15dk) parametreleri.
const ARALIK_HARITASI = {
  '12h': { saat: 12, aralik: '15dk' },
  '24h': { saat: 24, aralik: '15dk' },
  '3d': { saat: 72, aralik: 'saat' },
  '7d': { saat: 168, aralik: 'saat' },
  '30d': { saat: 720, aralik: 'saat' },
}

function araligiCoz(rangeValue) {
  const eslesme = ARALIK_HARITASI[rangeValue] ?? ARALIK_HARITASI['24h']
  const bitis = new Date()
  const baslangic = new Date(bitis.getTime() - eslesme.saat * 3600_000)
  return { baslangic: baslangic.toISOString(), bitis: bitis.toISOString(), aralik: eslesme.aralik }
}

// GET /api/hatlar/{hat_id}/trend -> tek hat trend noktaları. toplam_kisi,
// backend'in döndürdüğü ortalama_kisi × olcum_sayisi'dir — kovadaki tüm
// ölçümlerin toplamı (grafik ve "Toplam" etiketi bu alanı kullanır, ikisi
// aynı birimde olsun diye; ortalama_kisi tek başına "bir ölçümdeki ortalama
// kişi sayısı" anlamına geldiği için doğrudan toplanamaz).
async function tekHatTrendi(hatId, rangeValue) {
  const { baslangic, bitis, aralik } = araligiCoz(rangeValue)
  const q = new URLSearchParams({ baslangic, bitis, aralik })
  const noktalar = await apiGet(`/api/hatlar/${hatId}/trend?${q.toString()}`)
  return noktalar.map((n) => ({
    ...n,
    toplam_kisi: n.ortalama_kisi * n.olcum_sayisi,
  }))
}

// "Tüm Hatlar": backend'de agregasyon endpoint'i yok — N hat için paralel
// fetch + zaman kovalarına göre toplama (toplam_kisi doğrudan toplanır,
// ortalama_doluluk olcum_sayisi ağırlıklı ortalama kalır).
export async function trendGetir(hatId, rangeValue, tumHatlar = []) {
  if (hatId && hatId !== 'all') {
    return tekHatTrendi(hatId, rangeValue)
  }
  if (tumHatlar.length === 0) return []

  const sonuclar = await Promise.all(
    tumHatlar.map((h) => tekHatTrendi(h.hat_id, rangeValue))
  )
  const kovaMap = new Map() // zaman ISO -> { toplamKisi, doluluk, doluluk_n, olcum }
  for (const noktalar of sonuclar) {
    for (const n of noktalar) {
      const mevcut = kovaMap.get(n.zaman) ?? { toplamKisi: 0, doluluk: 0, doluluk_n: 0, olcum: 0 }
      mevcut.toplamKisi += n.toplam_kisi
      if (n.ortalama_doluluk != null) {
        mevcut.doluluk += n.ortalama_doluluk * n.olcum_sayisi
        mevcut.doluluk_n += n.olcum_sayisi
      }
      mevcut.olcum += n.olcum_sayisi
      kovaMap.set(n.zaman, mevcut)
    }
  }
  return [...kovaMap.entries()]
    .sort(([a], [b]) => new Date(a) - new Date(b))
    .map(([zaman, v]) => ({
      zaman,
      toplam_kisi: v.toplamKisi,
      ortalama_doluluk: v.doluluk_n ? v.doluluk / v.doluluk_n : null,
      olcum_sayisi: v.olcum,
    }))
}
