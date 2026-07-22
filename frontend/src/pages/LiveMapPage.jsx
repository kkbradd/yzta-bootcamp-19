import { useClock } from '../hooks/useClock'
import CanliHarita from '../components/CanliHarita'

export default function LiveMapPage({ onNavigate }) {
  const time = useClock()

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
              { key: 'live-map', label: 'Canlı Harita', icon: '🗺', active: true },
              { key: 'lines', label: 'Hatlar', icon: '⊟' },
              { key: 'stops', label: 'Duraklar', icon: '📍' },
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

        <div style={s.content}>
          <div style={s.mapCard}>
            <div style={s.cardHeader}>
              <div>
                <div style={s.cardTitle}>Canlı Harita</div>
                <div style={s.cardSubtitle}>Gerçek zamanlı araç doluluk oranları ve durak durumu</div>
              </div>
            </div>
            <div style={{ flex: 1, minHeight: 0 }}>
              <CanliHarita />
            </div>
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
  navItem: { display: 'flex', alignItems: 'center', gap: '10px', padding: '9px 12px', borderRadius: '8px', background: 'none', border: 'none', color: '#6b7280', fontSize: '14px', fontWeight: '500', cursor: 'pointer', width: '100%', textAlign: 'left', transition: 'background 0.15s' },
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
  content: { flex: 1, overflow: 'hidden', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' },
  mapCard: { flex: 1, minHeight: 0, background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexShrink: 0 },
  cardTitle: { fontSize: '14px', fontWeight: '700', color: '#111827' },
  cardSubtitle: { fontSize: '12px', color: '#9ca3af', marginTop: '2px' },
  footer: { padding: '12px 24px', borderTop: '1px solid #e5e7eb', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#9ca3af', flexShrink: 0 },
  footerLink: { color: '#9ca3af', textDecoration: 'none' },
}
