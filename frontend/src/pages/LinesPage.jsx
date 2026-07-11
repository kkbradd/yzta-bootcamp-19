import { useEffect, useState } from 'react'
import { useClock } from '../hooks/useClock'
import { hatlariGetir } from '../api/hatlar'
import { API_TABANI } from '../api/client'

// Mock veri — SİLİNMEDİ; backend'e ulaşılamazsa yedek (demo) olarak kullanılır.
const lines = [
  { code: '501', route: 'Üniversite - Şehir Terminali', duration: 45, stops: 24, buses: 8, status: 'orta' },
  { code: '34A', route: 'Sanayi Mahallesi - Hastane', duration: 35, stops: 18, buses: 5, status: 'yuksek' },
  { code: '12K', route: 'Körfez Evleri - Kent Meydanı', duration: 60, stops: 32, buses: 12, status: 'dusuk' },
  { code: '202', route: 'Havaalanı - Şehir Merkezi', duration: 30, stops: 12, buses: 4, status: 'orta' },
  { code: '60T', route: 'Toki Konutları - Batı Garajı', duration: 75, stops: 42, buses: 15, status: 'yuksek' },
  { code: '7B', route: 'İstasyon - Kültür Merkezi', duration: 25, stops: 15, buses: 3, status: 'dusuk' },
]

const statusConfig = {
  yuksek:  { label: 'Yüksek Doluluk', bg: '#fef2f2', color: '#ef4444', border: '#ef4444' },
  orta:    { label: 'Orta Doluluk',   bg: '#fffbeb', color: '#f59e0b', border: '#f59e0b' },
  dusuk:   { label: 'Düşük Doluluk',  bg: '#f0fdf4', color: '#22c55e', border: '#22c55e' },
  veriyok: { label: 'Veri Yok',       bg: '#f3f4f6', color: '#9ca3af', border: '#d1d5db' },
}

// Mock 'lines' -> kart şekli (backend başarısız olursa yedek olarak render edilir).
const DEMO_HATLAR = lines.map((l) => ({
  hat_id: l.code, code: l.code, route: l.route, buses: l.buses, durum: l.status,
}))

export default function LinesPage({ onNavigate }) {
  const time = useClock()
  const [search, setSearch] = useState('')
  const [hatlar, setHatlar] = useState([])
  const [asama, setAsama] = useState('yukleniyor') // 'yukleniyor' | 'hazir' | 'demo'

  useEffect(() => {
    let iptal = false
    setAsama('yukleniyor')
    hatlariGetir()
      .then((veri) => { if (!iptal) { setHatlar(veri); setAsama('hazir') } })
      .catch(() => { if (!iptal) { setHatlar(DEMO_HATLAR); setAsama('demo') } })
    return () => { iptal = true }
  }, [])

  const filtered = hatlar.filter((l) =>
    l.code.toLowerCase().includes(search.toLowerCase()) ||
    l.route.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={s.root}>
      {/* Sidebar */}
      <div style={s.sidebar}>
        <div style={s.sidebarTop}>
          <div style={s.logo}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#111827" strokeWidth="2.5">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
            <span style={s.logoText}>YOTAY</span>
          </div>

          <nav style={s.nav}>
            {[
              { key: 'dashboard', label: 'Dashboard', icon: '⊞' },
              { key: 'live-map',  label: 'Canlı Harita', icon: '🗺' },
              { key: 'lines',     label: 'Hatlar', icon: '⊟', active: true },
              { key: 'stops',     label: 'Duraklar', icon: '📍' },
            ].map(item => (
              <div
                key={item.key}
                style={{ ...s.navItem, ...(item.active ? s.navItemActive : {}) }}
                onClick={() => onNavigate && onNavigate(item.key)}
              >
                <span style={s.navIcon}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
            ))}
          </nav>
        </div>

        <div style={s.sidebarBottom}>
          <div style={s.navItem}>
            <span style={s.navIcon}>👤</span>
            <span>Admin</span>
          </div>
          <div style={{ ...s.navItem, cursor: 'pointer' }} onClick={() => onNavigate && onNavigate('logout')}>
            <span style={s.navIcon}>→</span>
            <span>Çıkış Yap</span>
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={s.main}>
        {/* Topbar */}
        <div style={s.topbar}>
          <div style={s.topbarLeft}>
            <div style={s.statusBadge}>
              <span style={s.statusDot} />
              Sistem Aktif
            </div>
            <div style={s.topbarDivider} />
            <div style={s.topbarMeta}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              142 Aktif Hat
            </div>
            <div style={s.topbarMeta}>
              <span style={{ color: '#f59e0b' }}>⚠</span>
              3 Çevrim Dışı
            </div>
          </div>
          <div style={s.topbarRight}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#9ca3af', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Son Güncelleme</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#111827' }}>⏱ {time}</div>
            </div>
            <div style={s.avatar}>A</div>
          </div>
        </div>

        {/* Content */}
        <div style={s.content}>
          {/* Page header + search */}
          <div style={s.pageHeader}>
            <div>
              <h1 style={s.pageTitle}>Hatlar</h1>
              <p style={s.pageSubtitle}>Sistemdeki tüm ulaşım hatlarını yönetin ve izleyin.</p>
            </div>
            <div style={s.searchWrapper}>
              <svg style={s.searchIcon} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                style={s.searchInput}
                placeholder="Hat Ara (Kod veya İsim)..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>

          {/* Durumlar / grid */}
          {asama === 'yukleniyor' && <div style={s.durumKutu}>Hatlar yükleniyor…</div>}
          {asama === 'demo' && (
            <div style={s.demoBanner}>
              Backend'e ulaşılamadı — demo verisi gösteriliyor ({API_TABANI})
            </div>
          )}
          {asama !== 'yukleniyor' && filtered.length === 0 && (
            <div style={s.durumKutu}>Hat bulunamadı.</div>
          )}
          {asama !== 'yukleniyor' && filtered.length > 0 && (
            <div style={s.grid}>
              {filtered.map(line => {
                const st = statusConfig[line.durum]
                return (
                  <div key={line.hat_id} style={{ ...s.card, borderLeftColor: st.border }}>
                    <div style={s.cardTop}>
                      <div style={s.cardTopLeft}>
                        <div style={s.busIconWrap}>
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                            <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                            <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
                          </svg>
                        </div>
                        <div>
                          <div style={s.lineCode}>{line.code}</div>
                          <div style={s.lineCodeLabel}>HAT KODU</div>
                        </div>
                      </div>
                      <span style={{ ...s.statusBadgeCard, background: st.bg, color: st.color }}>{st.label}</span>
                    </div>

                    <div style={s.cardDivider} />

                    <div style={s.routeName}>{line.route}</div>
                    <div style={s.duration}>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                      </svg>
                      Ortalama Sefer Süresi: —
                    </div>

                    <div style={s.cardDivider} />

                    <div style={s.stats}>
                      <div>
                        <div style={s.statLabel}>DURAK SAYISI</div>
                        <div style={s.statValue}>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                          </svg>
                          —
                        </div>
                      </div>
                      <div>
                        <div style={s.statLabel}>AKTİF OTOBÜS</div>
                        <div style={s.statValue}>
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                            <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                            <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
                          </svg>
                          {line.buses}
                        </div>
                      </div>
                    </div>

                    <div style={s.cardDivider} />

                    <div style={s.cardFooter}>
                      <span style={s.detailLink}>Detayları Görüntüle</span>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                        <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                      </svg>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <footer style={s.footer}>
          <span>© 2026 YOTAY — Belediye Operasyon Merkezi</span>
          <div style={{ display: 'flex', gap: '16px' }}>
            <a href="#" style={s.footerLink}>Kullanım Şartları</a>
            <a href="#" style={s.footerLink}>Gizlilik Politikası</a>
            <a href="#" style={s.footerLink}>Destek</a>
          </div>
        </footer>
      </div>
    </div>
  )
}

const s = {
  root: { display: 'flex', height: '100vh', width: '100vw', background: '#f9fafb', overflow: 'hidden' },
  sidebar: { width: '220px', flexShrink: 0, background: '#ffffff', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', padding: '20px 0' },
  sidebarTop: { display: 'flex', flexDirection: 'column', flex: 1 },
  sidebarBottom: { padding: '12px', borderTop: '1px solid #f3f4f6', display: 'flex', flexDirection: 'column', gap: '2px' },
  logo: { display: 'flex', alignItems: 'center', gap: '8px', padding: '0 20px 24px', borderBottom: '1px solid #f3f4f6' },
  logoText: { color: '#111827', fontWeight: '700', fontSize: '20px', letterSpacing: '0.02em' },
  nav: { flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '2px' },
  navItem: { display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 12px', borderRadius: '8px', color: '#6b7280', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
  navItemActive: { background: '#f3f4f6', color: '#111827', fontWeight: '600' },
  navIcon: { fontSize: '16px', width: '20px', textAlign: 'center' },
  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  topbar: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 24px', background: '#ffffff', borderBottom: '1px solid #e5e7eb', flexShrink: 0 },
  topbarLeft: { display: 'flex', alignItems: 'center', gap: '16px' },
  topbarRight: { display: 'flex', alignItems: 'center', gap: '14px' },
  statusBadge: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: '500', color: '#111827' },
  statusDot: { width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 0 2px #d1fae5' },
  topbarDivider: { width: '1px', height: '16px', background: '#e5e7eb' },
  topbarMeta: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#6b7280' },
  avatar: { width: '34px', height: '34px', borderRadius: '50%', background: '#111827', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: '600' },
  content: { flex: 1, overflow: 'auto', padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: '24px' },
  durumKutu: { padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '14px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: '12px' },
  demoBanner: { padding: '10px 14px', fontSize: '13px', color: '#92400e', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '10px' },
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' },
  pageTitle: { fontSize: '26px', fontWeight: '700', color: '#111827', marginBottom: '4px' },
  pageSubtitle: { fontSize: '14px', color: '#6b7280' },
  searchWrapper: { position: 'relative', display: 'flex', alignItems: 'center' },
  searchIcon: { position: 'absolute', left: '12px', pointerEvents: 'none' },
  searchInput: { padding: '10px 14px 10px 36px', border: '1px solid #e5e7eb', borderRadius: '10px', fontSize: '14px', color: '#111827', background: '#fff', outline: 'none', width: '260px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' },
  card: { background: '#ffffff', border: '1px solid #e5e7eb', borderLeft: '4px solid', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px', cursor: 'pointer' },
  cardTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' },
  cardTopLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  busIconWrap: { width: '40px', height: '40px', background: '#f3f4f6', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  lineCode: { fontSize: '22px', fontWeight: '700', color: '#111827' },
  lineCodeLabel: { fontSize: '10px', fontWeight: '600', color: '#9ca3af', letterSpacing: '0.05em' },
  statusBadgeCard: { fontSize: '11px', fontWeight: '600', padding: '4px 10px', borderRadius: '999px' },
  cardDivider: { height: '1px', background: '#f3f4f6' },
  routeName: { fontSize: '14px', fontWeight: '600', color: '#111827' },
  duration: { display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', color: '#9ca3af' },
  stats: { display: 'flex', gap: '32px' },
  statLabel: { fontSize: '10px', fontWeight: '600', color: '#9ca3af', letterSpacing: '0.05em', marginBottom: '4px' },
  statValue: { display: 'flex', alignItems: 'center', gap: '5px', fontSize: '15px', fontWeight: '600', color: '#111827' },
  cardFooter: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  detailLink: { fontSize: '13px', color: '#374151', fontWeight: '500' },
  footer: { padding: '12px 24px', borderTop: '1px solid #e5e7eb', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#9ca3af', flexShrink: 0 },
  footerLink: { color: '#9ca3af', textDecoration: 'none' },
}
