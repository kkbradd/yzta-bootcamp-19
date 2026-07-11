// Backend base URL — Docker/derleme anında VITE_API_URL ile gömülür (varsayılan :8000).
export const API_TABANI = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
