import { useState } from 'react'
import { LangProvider } from './context/LangContext'
import Navbar from './components/Navbar'
import Chatbot from './components/Chatbot'
import HomePage from './pages/HomePage'
import HotPage from './pages/HotPage'
import MapPage from './pages/MapPage'
import { useLang } from './context/LangContext'

// Inner app needs LangContext, so we split into AppInner
function AppInner() {
  const { lang } = useLang()
  const [page, setPage]               = useState('home')
  const [pendingMsg, setPendingMsg]   = useState(null)

  // Called when user clicks a property card
  const handleAskBot = (prop) => {
    const name = lang === 'en' ? prop.name_en
               : lang === 'vi' ? prop.name_vi
               : prop.name_ja

    const q = lang === 'ja' ? `「${name}」について詳しく教えてください`
            : lang === 'en' ? `Tell me more about "${name}"`
            : `Cho tôi biết thêm về "${name}"`

    setPendingMsg(q)
  }

  const showPage = (key) => {
    setPage(key)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div style={{ paddingTop: 'var(--nav-h)' }}>
      {/* Sticky navbar */}
      <Navbar page={page} setPage={showPage} />

      {/* Page content */}
      {page === 'home' && (
        <HomePage setPage={showPage} onAskBot={handleAskBot} />
      )}
      {page === 'hot' && (
        <HotPage onAskBot={handleAskBot} />
      )}
      {page === 'map' && (
        <MapPage />
      )}

      {/* Floating chatbot — always present */}
      <Chatbot
        pendingMessage={pendingMsg}
        onPendingConsumed={() => setPendingMsg(null)}
      />
    </div>
  )
}

export default function App() {
  return (
    <LangProvider>
      <AppInner />
    </LangProvider>
  )
}
