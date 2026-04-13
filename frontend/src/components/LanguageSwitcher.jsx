import { useState, useRef, useEffect } from 'react'
import { useLang } from '../context/LangContext'
import i18n from '../data/i18n'
import styles from './LanguageSwitcher.module.css'

const LANG_OPTIONS = [
  { code: 'ja', flag: '🇯🇵', label: '日本語',      native: 'Japanese'    },
  { code: 'en', flag: '🇬🇧', label: 'English',      native: '英語'         },
  { code: 'vi', flag: '🇻🇳', label: 'Tiếng Việt',  native: 'ベトナム語'   },
]

export default function LanguageSwitcher() {
  const { lang, setLang } = useLang()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  // Close on outside click
  useEffect(() => {
    const handler = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const active = LANG_OPTIONS.find(l => l.code === lang)

  const select = (code) => {
    setLang(code)
    setOpen(false)
  }

  return (
    <div className={styles.wrap} ref={ref}>
      <button
        className={styles.trigger}
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
      >
        <span className={styles.flag}>{active.flag}</span>
        <span className={styles.name}>{active.label}</span>
        <span className={`${styles.arrow} ${open ? styles.arrowOpen : ''}`}>▾</span>
      </button>

      {open && (
        <div className={styles.dropdown}>
          {LANG_OPTIONS.map(opt => (
            <button
              key={opt.code}
              className={`${styles.option} ${lang === opt.code ? styles.selected : ''}`}
              onClick={() => select(opt.code)}
            >
              <span className={styles.optFlag}>{opt.flag}</span>
              <span className={styles.optLabel}>{opt.label}</span>
              <span className={styles.optNative}>{opt.native}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
