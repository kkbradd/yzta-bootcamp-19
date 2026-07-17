import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import LiveMapPage from './pages/LiveMapPage'
import LinesPage from './pages/LinesPage'
import StopsPage from './pages/StopsPage'
import AsistanWidget from './components/AsistanWidget'
import './index.css'

function App() {
  const [page, setPage] = useState('login')
  const nav = (p) => setPage(p === 'logout' ? 'login' : p)

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
