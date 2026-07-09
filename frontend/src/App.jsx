import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import LiveMapPage from './pages/LiveMapPage'
import LinesPage from './pages/LinesPage'
import './index.css'

function App() {
  const [page, setPage] = useState('login')
  const nav = (p) => setPage(p === 'logout' ? 'login' : p)

  if (page === 'login') return <LoginPage onLogin={() => setPage('dashboard')} />
  if (page === 'live-map') return <LiveMapPage onNavigate={nav} />
  if (page === 'lines') return <LinesPage onNavigate={nav} />
  return <DashboardPage onNavigate={nav} />
}

export default App
