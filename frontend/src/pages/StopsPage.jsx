import { useState } from 'react'
import { useClock } from '../hooks/useClock'

const stops = [
  { code: 'D-1024', name: 'Atatürk Meydanı', address: 'Merkez, Cumhuriyet Bulvarı', lines: ['Hat 5', 'Hat 12', 'Hat 24', 'M1'], occupancy: 85, accessible: true, wifi: true, digital: true },
  { code: 'D-2105', name: 'Şehir Hastanesi', address: 'Sağlık Mah. Hastane Yolu', lines: ['Hat 7', 'Hat 8', 'Hat 11', 'H1'], occupancy: 60, accessible: true, wifi: true, digital: true },
  { code: 'D-3042', name: 'Teknokent Girişi', address: 'Üniversite Kampüsü', lines: ['Hat 5', 'Hat 12', 'Hat 15'], occupancy: 30, accessible: true, wifi: true, digital: true },
  { code: 'D-0921', name: 'Mavi Durak', address: 'Öğrenci Köyü Yolu', lines: ['Hat 1', 'Hat 5', 'Hat 22'], occupancy: 45, accessible: false, wifi: false, digital: true },
  { code: 'D-4410', name: 'Sanayi Sitesi', address: 'Organize Sanayi Bölgesi', lines: ['Hat 2', 'Hat 18', 'Hat 31'], occupancy: 75, accessible: true, wifi: false, digital: true },
  { code: 'D-5522', name: 'Marina Evleri', address: 'Kıyıboyu Cad. Sahil', lines: ['Hat 9', 'Hat 12', 'S1'], occupancy: 20, accessible: true, wifi: true, digital: true },
  { code: 'D-1188', name: 'Kütüphane Meydanı', address: 'Eğitim Mah. Kitap Sokak', lines: ['Hat 5', 'Hat 14', 'Hat 16'], occupancy: 55, accessible: true, wifi: false, digital: false },
  { code: 'D-0001', name: 'Otogar Ana Çıkış', address: 'Şehirlerarası Terminal', lines: ['Hat 101', 'Hat 202', 'Hat 303'], occupancy: 95, accessible: true, wifi: true, digital: true },
]

function occupancyColor(pct) {
  if (pct >= 80) return '#ef4444'
  if (pct >= 50) return '#f59e0b'
  return '#22c55e'
}

function borderColor(pct) {
  if (pct >= 80) return '#ef4444'
  if (pct >= 50) return '#f59e0b'
  return '#22c55e'
}

export default function StopsPage({ onNavigate }) {
  const time = useClock()
  const [search, setSearch] = useState('')

  const filtered = stops.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.code.toLowerCase().includes(search.toLowerCase())
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
              { key: 'lines',     label: 'Hatlar', icon: '⊟' },
              { key: 'stops',     label: 'Duraklar', icon: '📍', active: true },
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
          {/* Page header */}
          <div style={s.pageHeader}>
            <div>
              <h1 style={s.pageTitle}>Duraklar</h1>
              <p style={s.pageSubtitle}>Toplam {stops.length} durak sistemde kayıtlı ve izleniyor.</p>
            </div>
            <div style={s.headerRight}>
              <div style={s.searchWrapper}>
                <svg style={s.searchIcon} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  style={s.searchInput}
                  placeholder="Durak Ara (İsim veya Kod)..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <button style={s.filterBtn}>Filtrele</button>
            </div>
          </div>

          {/* Grid */}
          <div style={s.grid}>
            {filtered.map(stop => (
              <div key={stop.code} style={{ ...s.card, borderLeftColor: borderColor(stop.occupancy) }}>
                <div style={s.cardTop}>
                  <div style={s.stopIcon}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                    </svg>
                  </div>
                  <span style={s.stopCode}>{stop.code}</span>
                </div>

                <div style={s.stopName}>{stop.name}</div>
                <div style={s.stopAddress}>
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                    <polygon points="3 11 22 2 13 21 11 13 3 11"/>
                  </svg>
                  {stop.address}
                </div>

                <div style={s.linesTags}>
                  {stop.lines.map(l => (
                    <span key={l} style={s.lineTag}>{l}</span>
                  ))}
                </div>

                <div style={s.cardDivider} />

                <div style={s.features}>
                  <span style={{ ...s.feature, color: stop.accessible ? '#111827' : '#d1d5db' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M8 12l2 2 4-4"/></svg>
                    Erişim
                  </span>
                  <span style={{ ...s.feature, color: stop.wifi ? '#111827' : '#d1d5db' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1"/></svg>
                    Wi-Fi
                  </span>
                  <span style={{ ...s.feature, color: stop.digital ? '#111827' : '#d1d5db' }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                    Dijital
                  </span>
                </div>

                <div style={s.cardDivider} />

                <div style={s.cardBottom}>
                  <div>
                    <div style={s.occupancyLabel}>DOLULUK</div>
                    <div style={{ ...s.occupancyValue, color: occupancyColor(stop.occupancy) }}>%{stop.occupancy}</div>
                  </div>
                  <div style={s.arrowBtn}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' },
  pageTitle: { fontSize: '26px', fontWeight: '700', color: '#111827', marginBottom: '4px' },
  pageSubtitle: { fontSize: '14px', color: '#6b7280' },
  headerRight: { display: 'flex', alignItems: 'center', gap: '10px' },
  searchWrapper: { position: 'relative', display: 'flex', alignItems: 'center' },
  searchIcon: { position: 'absolute', left: '12px', pointerEvents: 'none' },
  searchInput: { padding: '10px 14px 10px 36px', border: '1px solid #e5e7eb', borderRadius: '10px', fontSize: '14px', color: '#111827', background: '#fff', outline: 'none', width: '260px' },
  filterBtn: { padding: '10px 18px', background: '#111827', color: 'white', border: 'none', borderRadius: '10px', fontSize: '14px', fontWeight: '500', cursor: 'pointer' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' },
  card: { background: '#ffffff', border: '1px solid #e5e7eb', borderLeft: '4px solid', borderRadius: '12px', padding: '18px', display: 'flex', flexDirection: 'column', gap: '10px', cursor: 'pointer' },
  cardTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  stopIcon: { width: '36px', height: '36px', background: '#f3f4f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  stopCode: { fontSize: '12px', fontWeight: '600', color: '#9ca3af' },
  stopName: { fontSize: '15px', fontWeight: '700', color: '#111827' },
  stopAddress: { display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px', color: '#9ca3af' },
  linesTags: { display: 'flex', flexWrap: 'wrap', gap: '6px' },
  lineTag: { fontSize: '11px', fontWeight: '500', background: '#f3f4f6', color: '#374151', padding: '3px 8px', borderRadius: '6px' },
  cardDivider: { height: '1px', background: '#f3f4f6' },
  features: { display: 'flex', gap: '14px' },
  feature: { display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: '500' },
  cardBottom: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  occupancyLabel: { fontSize: '10px', fontWeight: '600', color: '#9ca3af', letterSpacing: '0.05em', marginBottom: '2px' },
  occupancyValue: { fontSize: '16px', fontWeight: '700' },
  arrowBtn: { width: '28px', height: '28px', border: '1px solid #e5e7eb', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  footer: { padding: '12px 24px', borderTop: '1px solid #e5e7eb', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#9ca3af', flexShrink: 0 },
  footerLink: { color: '#9ca3af', textDecoration: 'none' },
}
