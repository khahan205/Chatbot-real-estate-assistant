import { useState, useRef, useEffect } from 'react'
import { useLang } from '../context/LangContext'
import properties from '../data/properties'
import styles from './Chatbot.module.css'

const PROP_CONTEXT = properties.map(p =>
  `• ${p.name_ja} (${p.name_en}) | ${p.type === 'rent' ? '賃貸' : '売却'} | ¥${p.price.toLocaleString()} | ${p.beds}LDK ${p.sqm}㎡ | ${p.loc} | ${p.built}年築`
).join('\n')

const SYSTEM_PROMPT = `You are HomeFind AI, a warm and expert bilingual (Japanese/English/Vietnamese) property advisor for a premium Japan real estate website.

Available properties:
${PROP_CONTEXT}

Response style:
- Detect the user's language and respond in that language
- Keep replies concise: 2-4 sentences
- Naturally blend light Japanese phrases (おすすめ, ありがとう, こちら) even in English/Vietnamese
- When recommending, name the property + price + one compelling detail
- End with a helpful follow-up question when appropriate
- Use ¥ for prices in 万 units (e.g., ¥6,800万)`

export default function Chatbot({ pendingMessage, onPendingConsumed }) {
  const { t } = useLang()
  const [open, setOpen]       = useState(false)
  const [input, setInput]     = useState('')
  const [messages, setMessages] = useState([])
  const [typing, setTyping]   = useState(false)
  const [chipsVisible, setChipsVisible] = useState(true)
  const historyRef = useRef([])
  const msgsRef    = useRef(null)

  // Scroll to bottom on new message
  useEffect(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight
  }, [messages, typing])

  // Handle incoming message from card click
  useEffect(() => {
    if (pendingMessage) {
      setOpen(true)
      setTimeout(() => {
        setInput(pendingMessage)
        handleSend(pendingMessage)
        onPendingConsumed()
      }, 350)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingMessage])

  const addMsg = (text, role) => {
    setMessages(prev => [...prev, { text, role, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
  }

  const handleSend = async (overrideText) => {
    const text = (overrideText ?? input).trim()
    if (!text) return
    setInput('')
    setChipsVisible(false)
    addMsg(text, 'user')
    historyRef.current.push({ role: 'user', content: text })
    setTyping(true)

    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1000,
          system: SYSTEM_PROMPT,
          messages: historyRef.current,
        }),
      })
      const data = await res.json()
      const reply = data.content?.map(b => b.text || '').join('') || '申し訳ありません。もう一度お試しください。'
      setTyping(false)
      addMsg(reply, 'bot')
      historyRef.current.push({ role: 'assistant', content: reply })
    } catch {
      setTyping(false)
      addMsg('申し訳ありません — もう一度お試しください 🙏', 'bot')
    }
  }

  const chips = [t.chip1, t.chip2, t.chip3, t.chip4]

  const greetingText = t.chat_greeting

  return (
    <>
      {/* FAB button */}
      <button
        className={styles.fab}
        onClick={() => setOpen(o => !o)}
        aria-label="AI Chat"
      >
        <span>{open ? '✕' : '🤖'}</span>
        <div className={styles.fabBadge}>AI</div>
      </button>

      {/* Chat window */}
      <div className={`${styles.window} ${open ? styles.windowOpen : ''}`}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.avatar}>🏡</div>
          <div className={styles.headerInfo}>
            <div className={styles.headerTitle}>HomeFind AI</div>
            <div className={styles.headerSub}>{t.chat_sub}</div>
          </div>
          <div className={styles.statusDot} />
          <button className={styles.closeBtn} onClick={() => setOpen(false)}>✕</button>
        </div>

        {/* Messages */}
        <div className={styles.messages} ref={msgsRef}>
          {/* Greeting */}
          <div className={`${styles.msg} ${styles.bot}`}>
            <div className={styles.bubble}>
              {greetingText.split('\n').map((line, i) => (
                <span key={i}>{line}{i < greetingText.split('\n').length - 1 && <br />}</span>
              ))}
            </div>
            <div className={styles.time}>Now</div>
          </div>

          {messages.map((m, i) => (
            <div key={i} className={`${styles.msg} ${styles[m.role]}`}>
              <div className={styles.bubble}>{m.text}</div>
              <div className={styles.time}>{m.time}</div>
            </div>
          ))}

          {typing && (
            <div className={`${styles.msg} ${styles.bot}`}>
              <div className={styles.typingWrap}>
                <span className={styles.dot} />
                <span className={styles.dot} />
                <span className={styles.dot} />
              </div>
            </div>
          )}
        </div>

        {/* Chips */}
        {chipsVisible && (
          <div className={styles.chips}>
            {chips.map((chip, i) => (
              <button
                key={i}
                className={styles.chip}
                onClick={() => { setInput(chip); handleSend(chip) }}
              >
                {chip}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className={styles.inputRow}>
          <input
            className={styles.input}
            value={input}
            placeholder={t.chat_ph}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
          />
          <button className={styles.sendBtn} onClick={() => handleSend()}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="13" height="13">
              <path d="M22 2L11 13" />
              <path d="M22 2L15 22 11 13 2 9l20-7z" />
            </svg>
          </button>
        </div>

        <div className={styles.powered}>Powered by Claude AI · Claude AIが対応</div>
      </div>
    </>
  )
}
