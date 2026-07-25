import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import LiveMapPage from './pages/LiveMapPage'
import LinesPage from './pages/LinesPage'
import StopsPage from './pages/StopsPage'
import AsistanTestPage from './pages/AsistanTestPage'
import AsistanWidget from './components/AsistanWidget'
import './index.css'

// Ekip içi asistan deneme ekranı: #asistan ile doğrudan açılır, oturum istemez.
// Yönlendirici kurmamak için hash kontrolü yeterli (tek ek ekran).
const ASISTAN_TEST_HASHI = '#asistan'

function App() {
  const [page, setPage] = useState('login')
  const nav = (p) => setPage(p === 'logout' ? 'login' : p)

  if (window.location.hash === ASISTAN_TEST_HASHI) return <AsistanTestPage />

  // Asistan yalnız oturum açıldıktan sonra; giriş ekranında gösterilmez.
  if (page === 'login') return <LoginPage onLogin={() => setPage('dashboard')} />

  return (
    <>
      {page === 'live-map' && <LiveMapPage onNavigate={nav} />}
      {page === 'lines' && <LinesPage onNavigate={nav} />}
      {page === 'stops' && <StopsPage onNavigate={nav} />}
      {!['live-map', 'lines', 'stops'].includes(page) && <DashboardPage onNavigate={nav} />}
      <AsistanWidget />
    </>
  )
}

export default App
