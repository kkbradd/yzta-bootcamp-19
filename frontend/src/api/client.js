// Backend base URL — Docker/derleme anında VITE_API_URL ile gömülür (varsayılan :8000).
export const API_TABANI = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Asistan servisi ayrı port'ta çalışır (varsayılan :8100); o da derleme anında gömülür.
export const ASISTAN_TABANI = import.meta.env.VITE_ASISTAN_URL || 'http://localhost:8100'

// Basit GET sarmalayıcı: JSON döndürür, HTTP hatasında fırlatır.
export async function apiGet(yol) {
  const yanit = await fetch(`${API_TABANI}${yol}`, {
    headers: { Accept: 'application/json' },
  })
  if (!yanit.ok) {
    throw new Error(`İstek başarısız: ${yanit.status}`)
  }
  return yanit.json()
}

// Basit POST sarmalayıcı: JSON gönderir, JSON döndürür, HTTP hatasında fırlatır.
export async function apiPost(yol, govde, taban = API_TABANI) {
  const yanit = await fetch(`${taban}${yol}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(govde),
  })
  if (!yanit.ok) {
    throw new Error(`İstek başarısız: ${yanit.status}`)
  }
  return yanit.json()
}
