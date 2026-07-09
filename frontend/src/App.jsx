import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import './index.css'

function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  return loggedIn ? <DashboardPage /> : <LoginPage onLogin={() => setLoggedIn(true)} />
}

export default App
