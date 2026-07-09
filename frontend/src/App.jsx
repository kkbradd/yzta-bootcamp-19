import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import LiveMapPage from './pages/LiveMapPage'
import './index.css'

function App() {
  const [page, setPage] = useState('login')

  if (page === 'login') return <LoginPage onLogin={() => setPage('dashboard')} />
  if (page === 'live-map') return <LiveMapPage onNavigate={(p) => setPage(p === 'logout' ? 'login' : p)} />
  return <DashboardPage onNavigate={(p) => setPage(p === 'logout' ? 'login' : p)} />
}

export default App
