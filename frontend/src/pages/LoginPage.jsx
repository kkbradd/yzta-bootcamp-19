import { useState } from 'react'
import { apiPost } from '../api/client'
const busBg = '/otobus.png'

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [hata, setHata] = useState('')
  const [gonderiliyor, setGonderiliyor] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setHata('')
    setGonderiliyor(true)
    try {
      const yanit = await apiPost('/api/oturum', { eposta: email, sifre: password })
      localStorage.setItem('erisim_tokeni', yanit.erisim_tokeni)
      if (onLogin) onLogin()
    } catch {
      setHata('E-posta veya şifre hatalı.')
    } finally {
      setGonderiliyor(false)
    }
  }

  return (
    <div style={styles.root}>
      {/* Sol panel */}
      <div style={styles.left}>
        <div style={styles.overlay} />
        <div style={styles.leftContent}>
          <div style={styles.logo}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
            <span style={styles.logoText}>YOTAY</span>
          </div>

          <div style={styles.hero}>
            <h1 style={styles.heroTitle}>
              Şehir içi ulaşımın{' '}
              <span style={styles.heroHighlight}>akıllı</span>
              <br />
              <span style={styles.heroBlue}>geleceği</span> burada başlıyor.
            </h1>
            <p style={styles.heroDesc}>
              AI destekli gerçek zamanlı takip, doluluk analizi ve hat yönetimi
              ile belediye ulaşım operasyonlarınızı tek bir merkezden optimize edin.
            </p>
          </div>

          <div style={styles.footer}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span style={styles.footerText}>T.C. Ulaştırma ve Altyapı Bakanlığı ile Uyumlu</span>
          </div>
        </div>
      </div>

      {/* Sağ panel */}
      <div style={styles.right}>
        <div style={styles.formContainer}>
          <div style={styles.formHeader}>
            <h2 style={styles.formTitle}>Operatör Girişi</h2>
            <p style={styles.formSubtitle}>Lütfen yetkili hesabınızla sisteme giriş yapın.</p>
          </div>

          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Oturum Aç</h3>
            <p style={styles.cardSubtitle}>Kimlik bilgilerinizi aşağıya girin</p>

            <form onSubmit={handleSubmit} style={styles.form}>
              <div style={styles.fieldGroup}>
                <label style={styles.label}>E-posta</label>
                <div style={styles.inputWrapper}>
                  <svg style={styles.inputIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  <input
                    type="email"
                    placeholder="admin@demo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={styles.input}
                    required
                  />
                </div>
              </div>

              <div style={styles.fieldGroup}>
                <div style={styles.labelRow}>
                  <label style={styles.label}>Şifre</label>
                  <a href="#" style={styles.forgotLink}>Şifremi unuttum?</a>
                </div>
                <div style={styles.inputWrapper}>
                  <svg style={styles.inputIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={styles.input}
                    required
                  />
                </div>
              </div>

              {hata && <p style={styles.hata}>{hata}</p>}

              <button type="submit" style={styles.submitBtn} disabled={gonderiliyor}>
                {gonderiliyor ? 'Giriş yapılıyor…' : 'Giriş Yap'}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </button>
            </form>
          </div>

          <p style={styles.notice}>
            Sistem erişimi yalnızca kayıtlı belediye personeli ile sınırlıdır.
            Problem yaşıyorsanız <a href="#" style={styles.supportLink}>IT Destek</a> ile iletişime geçin.
          </p>

          <div style={styles.demoKutusu}>
            <span style={styles.demoBaslik}>Demo giriş bilgileri</span>
            <span>E-posta: admin@demo.com</span>
            <span>Şifre: admin123</span>
          </div>
        </div>
      </div>
    </div>
  )
}

const styles = {
  root: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    overflow: 'hidden',
  },
  left: {
    position: 'relative',
    flex: '0 0 55%',
    backgroundImage: `url(${busBg})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center bottom',
    display: 'flex',
    flexDirection: 'column',
  },
  overlay: {
    position: 'absolute',
    inset: 0,
    background: 'linear-gradient(135deg, rgba(0,0,0,0.75) 0%, rgba(0,20,60,0.65) 100%)',
  },
  leftContent: {
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    padding: '36px 44px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  logoText: {
    color: 'white',
    fontWeight: '600',
    fontSize: '30px',
  },
  hero: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    gap: '20px',
  },
  heroTitle: {
    fontSize: '42px',
    fontWeight: '700',
    color: 'white',
    lineHeight: '1.2',
  },
  heroHighlight: {
    color: 'white',
  },
  heroBlue: {
    color: '#3b82f6',
  },
  heroDesc: {
    fontSize: '15px',
    color: 'rgba(255,255,255,0.75)',
    lineHeight: '1.6',
    maxWidth: '480px',
  },
  featureCards: {
    display: 'flex',
    gap: '14px',
    marginTop: '8px',
  },
  featureCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    background: 'rgba(255,255,255,0.12)',
    backdropFilter: 'blur(8px)',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '12px',
    padding: '14px 18px',
    flex: 1,
  },
  featureIcon: {
    fontSize: '22px',
  },
  featureTitle: {
    color: 'white',
    fontWeight: '600',
    fontSize: '14px',
  },
  featureDesc: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: '12px',
    marginTop: '2px',
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  footerText: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: '12px',
  },
  right: {
    flex: '0 0 45%',
    background: '#ffffff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px',
  },
  formContainer: {
    width: '100%',
    maxWidth: '560px',
    display: 'flex',
    flexDirection: 'column',
    gap: '28px',
  },
  formHeader: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  formTitle: {
    fontSize: '34px',
    fontWeight: '700',
    color: '#111827',
  },
  formSubtitle: {
    fontSize: '15px',
    color: '#6b7280',
  },
  card: {
    background: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '16px',
    padding: '44px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)',
  },
  cardTitle: {
    fontSize: '22px',
    fontWeight: '600',
    color: '#111827',
    marginBottom: '6px',
  },
  cardSubtitle: {
    fontSize: '15px',
    color: '#9ca3af',
    marginBottom: '32px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '22px',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '7px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
  },
  labelRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  inputWrapper: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  inputIcon: {
    position: 'absolute',
    left: '14px',
    pointerEvents: 'none',
  },
  input: {
    width: '100%',
    padding: '15px 16px 15px 44px',
    border: '1px solid #e5e7eb',
    borderRadius: '10px',
    fontSize: '15px',
    color: '#111827',
    outline: 'none',
    transition: 'border-color 0.2s',
    background: '#fafafa',
  },
  forgotLink: {
    fontSize: '13px',
    color: '#6b7280',
    textDecoration: 'none',
  },
  hata: {
    fontSize: '13px',
    color: '#dc2626',
    margin: 0,
  },
  demoKutusu: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    padding: '14px 16px',
    background: '#f9fafb',
    border: '1px dashed #d1d5db',
    borderRadius: '10px',
    fontSize: '13px',
    color: '#6b7280',
  },
  demoBaslik: {
    fontWeight: '600',
    color: '#374151',
    marginBottom: '2px',
  },
  submitBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '17px',
    background: '#111827',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    marginTop: '4px',
    transition: 'background 0.2s',
  },
  notice: {
    fontSize: '13px',
    color: '#9ca3af',
    textAlign: 'center',
    lineHeight: '1.6',
  },
  supportLink: {
    color: '#374151',
    fontWeight: '500',
    textDecoration: 'none',
  },
}
