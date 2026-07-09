import { useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

const generateData = (points, multiplier = 1) => {
  const base = [800, 600, 500, 450, 420, 500, 1200, 3500, 6800, 8200, 7900, 7200,
    8500, 9100, 8800, 8200, 9500, 9800, 8600, 7200, 5800, 4200, 2800, 1400]
  return Array.from({ length: points }, (_, i) => ({
    time: i,
    value: Math.round((base[i % base.length] + Math.random() * 300) * multiplier)
  }))
}

const timeRanges = [
  { label: '12 Saat', value: '12h', points: 12, multiplier: 1 },
  { label: '24 Saat', value: '24h', points: 24, multiplier: 1 },
  { label: '3 Gün', value: '3d', points: 36, multiplier: 0.9 },
  { label: '7 Gün', value: '7d', points: 42, multiplier: 1.1 },
  { label: '30 Gün', value: '30d', points: 30, multiplier: 1.2 },
]

const routes = [
  { label: 'Tüm Hatlar', value: 'all' },
  { label: 'Hat 1', value: '1' },
  { label: 'Hat 2', value: '2' },
  { label: 'Hat 3', value: '3' },
  { label: 'Hat 5', value: '5' },
  { label: 'Hat 12', value: '12' },
  { label: 'Hat 34', value: '34' },
]

const formatXAxis = (index, range) => {
  if (range === '12h' || range === '24h') {
    return `${String(index).padStart(2, '0')}:00`
  }
  if (range === '3d') return `Gün ${Math.floor(index / 12) + 1}`
  if (range === '7d') return `Gün ${Math.floor(index / 6) + 1}`
  return `${index + 1}. Gün`
}

const CustomTooltip = ({ active, payload, label, range }) => {
  if (active && payload && payload.length) {
    return (
      <div style={tooltipStyle}>
        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
          {formatXAxis(label, range)}
        </div>
        <div style={{ fontSize: '15px', fontWeight: '600', color: '#111827' }}>
          {payload[0].value.toLocaleString('tr-TR')} Yolcu
        </div>
      </div>
    )
  }
  return null
}

export default function DashboardPage({ onNavigate }) {
  const [selectedRange, setSelectedRange] = useState('24h')
  const [selectedRoute, setSelectedRoute] = useState('all')

  const currentRange = timeRanges.find(r => r.value === selectedRange)
  const data = generateData(currentRange.points, currentRange.multiplier)
  const totalPassengers = data.reduce((sum, d) => sum + d.value, 0)

  return (
    <div style={styles.root}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.sidebarLogo}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#111827" strokeWidth="2.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <span style={styles.sidebarLogoText}>YOTAY</span>
        </div>

        <nav style={styles.nav}>
          {[
            { icon: '⊞', label: 'Dashboard', active: true, key: 'dashboard' },
            { icon: '🗺', label: 'Canlı Harita', key: 'live-map' },
            { icon: '⊟', label: 'Hatlar', key: 'lines' },
            { icon: '📍', label: 'Duraklar', key: 'stops' },
          ].map(item => (
            <div key={item.label} style={{ ...styles.navItem, ...(item.active ? styles.navItemActive : {}), cursor: 'pointer' }}
              onClick={() => onNavigate && onNavigate(item.key)}>
              <span style={styles.navIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </nav>

        <div style={styles.sidebarBottom}>
          <div style={styles.navItem}>
            <span style={styles.navIcon}>👤</span>
            <span>Admin</span>
          </div>
          <div style={{ ...styles.navItem, cursor: 'pointer' }} onClick={() => onNavigate && onNavigate('logout')}>
            <span style={styles.navIcon}>→</span>
            <span>Çıkış Yap</span>
          </div>
        </div>
      </aside>

      {/* Ana içerik */}
      <main style={styles.main}>
        {/* Topbar */}
        <header style={styles.topbar}>
          <div style={styles.topbarLeft}>
            <div style={styles.statusBadge}>
              <span style={styles.statusDot} />
              Sistem Aktif
            </div>
            <div style={styles.topbarDivider} />
            <div style={styles.topbarMeta}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              142 Aktif Hat
            </div>
            <div style={styles.topbarMeta}>
              <span style={{ color: '#f59e0b' }}>⚠</span>
              3 Çevrim Dışı
            </div>
          </div>
          <div style={styles.topbarRight}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#9ca3af', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Son Güncelleme</div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#111827' }}>⏱ 14:32:05</div>
            </div>
            <div style={styles.avatar}>A</div>
          </div>
        </header>

        <div style={styles.content}>
          {/* KPI Kartları */}
          <div style={styles.kpiGrid}>
            {[
              { label: 'TOPLAM HAT', value: '142', change: '+2%', icon: '✈', color: '#3b82f6' },
              { label: 'AKTİF HAT', value: '138', change: '-%0.5', icon: '⊟', color: '#10b981' },
              { label: 'YOĞUN HAT', value: '12', change: '+12%', icon: '👥', color: '#8b5cf6' },
              { label: 'YOĞUN DURAK', value: '45', change: '+5%', icon: '📍', color: '#f59e0b' },
              { label: 'ORT. DOLULUK', value: '%64', change: '-3%', icon: '📉', color: '#ef4444' },
              { label: 'AKTİF ALARM', value: '3', change: 'Kritik', icon: '⏰', color: '#ef4444', critical: true },
            ].map(kpi => (
              <div key={kpi.label} style={styles.kpiCard}>
                <div style={styles.kpiTop}>
                  <div style={{ ...styles.kpiIcon, background: kpi.color + '15', color: kpi.color }}>{kpi.icon}</div>
                  <span style={{ ...styles.kpiBadge, background: kpi.critical ? '#fef2f2' : '#f9fafb', color: kpi.critical ? '#ef4444' : '#6b7280' }}>
                    {kpi.change}
                  </span>
                </div>
                <div style={styles.kpiLabel}>{kpi.label}</div>
                <div style={styles.kpiValue}>{kpi.value}</div>
              </div>
            ))}
          </div>

          <div style={styles.middleRow}>
            {/* Canlı Şehir Takibi */}
            <div style={styles.mapCard}>
              <div style={styles.cardHeader}>
                <div>
                  <div style={styles.cardTitle}>Canlı Harita</div>
                  <div style={styles.cardSubtitle}>Gerçek zamanlı araç doluluk oranları ve durak durumu</div>
                </div>
                <div style={styles.mapLegend}>
                  <span style={styles.legendDot('#10b981')} /> Düşük
                  <span style={styles.legendDot('#f59e0b')} /> Orta
                  <span style={styles.legendDot('#ef4444')} /> Yüksek
                </div>
              </div>
              <div style={styles.mapPlaceholder}>
                <div style={styles.mapPlaceholderIcon}>🗺</div>
                <div style={styles.mapPlaceholderText}>Harita görünümü</div>
                <div style={styles.mapPlaceholderSub}>Gerçek zamanlı harita entegrasyonu yakında</div>
              </div>
            </div>

            {/* Sağ panel */}
            <div style={styles.rightPanel}>
              {/* Son Uyarılar */}
              <div style={styles.card}>
                <div style={styles.cardHeaderRow}>
                  <div style={styles.cardTitle}>🔔 Son Uyarılar</div>
                  <a href="#" style={styles.linkBtn}>Tümünü Gör</a>
                </div>
                {[
                  { title: 'Hat 502', desc: 'Kaza nedeniyle güzergah değişikliği.', time: '14:45', color: '#ef4444' },
                  { title: 'Hat 12', desc: 'Araç arızası: Teknik ekip yönlendirildi.', time: '14:32', color: '#f59e0b' },
                  { title: 'Durak 104', desc: 'Yüksek yolcu yoğunluğu tespit edildi.', time: '14:10', color: '#3b82f6' },
                ].map(alert => (
                  <div key={alert.title} style={styles.alertItem}>
                    <div style={{ ...styles.alertBar, background: alert.color }} />
                    <div style={{ flex: 1 }}>
                      <div style={styles.alertTitle}>{alert.title}</div>
                      <div style={styles.alertDesc}>{alert.desc}</div>
                    </div>
                    <div style={styles.alertTime}>{alert.time}</div>
                  </div>
                ))}
              </div>

              {/* AI Önerileri */}
              <div style={styles.card}>
                <div style={styles.cardHeaderRow}>
                  <div style={styles.cardTitle}>🤖 AI Önerileri</div>
                </div>
                {[
                  { priority: 'High Priority', text: 'Hat 5 için yoğunluk nedeniyle 2 ek sefer planlanmalı.', color: '#ef4444', bg: '#fef2f2' },
                  { priority: 'Medium Priority', text: 'Üniversite durağındaki yığılma için Hat 102 yönlendirilmeli.', color: '#f59e0b', bg: '#fffbeb' },
                ].map(item => (
                  <div key={item.text} style={styles.aiItem}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <span style={{ ...styles.priorityBadge, background: item.bg, color: item.color }}>{item.priority}</span>
                      <span style={{ color: '#10b981', fontSize: '14px' }}>✓</span>
                    </div>
                    <div style={styles.aiText}>{item.text}</div>
                  </div>
                ))}
                <button style={styles.aiBtn}>Yeni Öneri Oluştur</button>
              </div>
            </div>
          </div>

          {/* Yolcu Yoğunluğu Trendi */}
          <div style={styles.chartCard}>
            <div style={styles.chartHeader}>
              <div>
                <div style={styles.cardTitle}>Yolcu Yoğunluğu Trendi</div>
                <div style={styles.cardSubtitle}>Tüm hatlar genelindeki yolcu sayısı değişimi</div>
              </div>
              <div style={styles.chartControls}>
                {/* Hat seçimi */}
                <select
                  value={selectedRoute}
                  onChange={e => setSelectedRoute(e.target.value)}
                  style={styles.select}
                >
                  {routes.map(r => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>

                {/* Zaman aralığı */}
                <div style={styles.rangeButtons}>
                  {timeRanges.map(r => (
                    <button
                      key={r.value}
                      onClick={() => setSelectedRange(r.value)}
                      style={{ ...styles.rangeBtn, ...(selectedRange === r.value ? styles.rangeBtnActive : {}) }}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#9ca3af' }}>Toplam</div>
                  <div style={{ fontSize: '15px', fontWeight: '700', color: '#111827' }}>
                    {totalPassengers.toLocaleString('tr-TR')} Yolcu
                  </div>
                </div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="passengerGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#111827" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#111827" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis
                  dataKey="time"
                  tickFormatter={i => formatXAxis(i, selectedRange)}
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  axisLine={false}
                  tickLine={false}
                  interval={Math.floor(data.length / 7)}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#9ca3af' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={v => v.toLocaleString('tr-TR')}
                />
                <Tooltip content={<CustomTooltip range={selectedRange} />} />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#111827"
                  strokeWidth={2}
                  fill="url(#passengerGradient)"
                  dot={false}
                  activeDot={{ r: 4, fill: '#111827' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <footer style={styles.footer}>
          <span>© 2026 YOTAY — Belediye Operasyon Merkezi</span>
          <div style={{ display: 'flex', gap: '16px' }}>
            <a href="#" style={styles.footerLink}>Kullanım Şartları</a>
            <a href="#" style={styles.footerLink}>Gizlilik Politikası</a>
            <a href="#" style={styles.footerLink}>Destek</a>
          </div>
        </footer>
      </main>
    </div>
  )
}

const tooltipStyle = {
  background: 'white',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '10px 14px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
}

const styles = {
  root: { display: 'flex', height: '100vh', width: '100vw', background: '#f9fafb', overflow: 'hidden' },
  sidebar: {
    width: '220px', flexShrink: 0, background: '#ffffff',
    borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', padding: '20px 0',
  },
  sidebarLogo: {
    display: 'flex', alignItems: 'center', gap: '8px',
    padding: '0 20px 24px', borderBottom: '1px solid #f3f4f6',
  },
  sidebarLogoText: { fontSize: '20px', fontWeight: '700', color: '#111827', letterSpacing: '0.02em' },
  nav: { flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: '2px' },
  navItem: {
    display: 'flex', alignItems: 'center', gap: '10px',
    padding: '9px 12px', borderRadius: '8px', cursor: 'pointer',
    fontSize: '14px', color: '#6b7280', fontWeight: '500',
  },
  navItemActive: { background: '#f3f4f6', color: '#111827', fontWeight: '600' },
  navIcon: { fontSize: '16px', width: '20px', textAlign: 'center' },
  sidebarBottom: { padding: '12px', borderTop: '1px solid #f3f4f6', display: 'flex', flexDirection: 'column', gap: '2px' },
  topbar: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '12px 24px', background: '#ffffff', borderBottom: '1px solid #e5e7eb',
    flexShrink: 0,
  },
  topbarLeft: { display: 'flex', alignItems: 'center', gap: '16px' },
  topbarRight: { display: 'flex', alignItems: 'center', gap: '14px' },
  statusBadge: {
    display: 'flex', alignItems: 'center', gap: '6px',
    fontSize: '13px', fontWeight: '500', color: '#111827',
  },
  statusDot: {
    width: '8px', height: '8px', borderRadius: '50%', background: '#10b981',
    display: 'inline-block', boxShadow: '0 0 0 2px #d1fae5',
  },
  topbarDivider: { width: '1px', height: '16px', background: '#e5e7eb' },
  topbarMeta: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#6b7280' },
  avatar: {
    width: '34px', height: '34px', borderRadius: '50%',
    background: '#111827', color: 'white', display: 'flex',
    alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: '600',
  },
  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  content: { flex: 1, overflow: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' },
  kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px' },
  kpiCard: {
    background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px',
    padding: '16px', display: 'flex', flexDirection: 'column', gap: '6px',
  },
  kpiTop: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' },
  kpiIcon: { width: '32px', height: '32px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' },
  kpiBadge: { fontSize: '11px', fontWeight: '600', padding: '2px 8px', borderRadius: '999px' },
  kpiLabel: { fontSize: '11px', color: '#9ca3af', fontWeight: '600', letterSpacing: '0.05em' },
  kpiValue: { fontSize: '26px', fontWeight: '700', color: '#111827', lineHeight: 1 },
  middleRow: { display: 'flex', gap: '16px', flex: '0 0 auto' },
  mapCard: { flex: 1, background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '20px' },
  rightPanel: { width: '280px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '12px' },
  card: { background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '16px' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' },
  cardHeaderRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' },
  cardTitle: { fontSize: '14px', fontWeight: '700', color: '#111827' },
  cardSubtitle: { fontSize: '12px', color: '#9ca3af', marginTop: '2px' },
  mapLegend: { display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px', color: '#6b7280' },
  legendDot: (color) => ({ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: color, marginRight: '4px' }),
  mapPlaceholder: {
    height: '340px', background: '#f9fafb', borderRadius: '10px',
    border: '2px dashed #e5e7eb', display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center', gap: '8px',
  },
  mapPlaceholderIcon: { fontSize: '40px', opacity: 0.3 },
  mapPlaceholderText: { fontSize: '14px', fontWeight: '600', color: '#9ca3af' },
  mapPlaceholderSub: { fontSize: '12px', color: '#d1d5db' },
  linkBtn: { fontSize: '12px', color: '#6b7280', textDecoration: 'none' },
  alertItem: { display: 'flex', alignItems: 'flex-start', gap: '10px', padding: '8px 0', borderTop: '1px solid #f3f4f6' },
  alertBar: { width: '3px', height: '36px', borderRadius: '2px', flexShrink: 0 },
  alertTitle: { fontSize: '13px', fontWeight: '600', color: '#111827' },
  alertDesc: { fontSize: '12px', color: '#6b7280', marginTop: '2px' },
  alertTime: { fontSize: '11px', color: '#9ca3af', flexShrink: 0 },
  aiItem: { background: '#f9fafb', borderRadius: '8px', padding: '10px', marginBottom: '8px' },
  aiText: { fontSize: '12px', color: '#374151', lineHeight: 1.5 },
  priorityBadge: { fontSize: '11px', fontWeight: '600', padding: '2px 8px', borderRadius: '999px' },
  aiBtn: {
    width: '100%', padding: '9px', background: '#111827', color: 'white',
    border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: '600', cursor: 'pointer',
  },
  chartCard: { background: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '20px' },
  chartHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' },
  chartControls: { display: 'flex', alignItems: 'center', gap: '12px' },
  select: {
    padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '8px',
    fontSize: '13px', color: '#374151', background: '#ffffff', cursor: 'pointer', outline: 'none',
  },
  rangeButtons: { display: 'flex', background: '#f3f4f6', borderRadius: '8px', padding: '3px' },
  rangeBtn: {
    padding: '5px 10px', border: 'none', borderRadius: '6px',
    fontSize: '12px', fontWeight: '500', color: '#6b7280', background: 'transparent', cursor: 'pointer',
  },
  rangeBtnActive: { background: '#ffffff', color: '#111827', fontWeight: '600', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  footer: {
    padding: '12px 24px', borderTop: '1px solid #e5e7eb', background: '#ffffff',
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    fontSize: '12px', color: '#9ca3af', flexShrink: 0,
  },
  footerLink: { color: '#9ca3af', textDecoration: 'none' },
}
