import { useLang } from '../context/LangContext'
import LanguageSwitcher from './LanguageSwitcher'
import styles from './Navbar.module.css'

export default function Navbar({ page, setPage }) {
  const { t } = useLang()

  const navItems = [
    { key: 'home', icon: '🏠', label: t.nav_home },
    { key: 'map',  icon: '🗺️', label: t.nav_map  },
    { key: 'hot',  icon: '🔥', label: t.nav_hot  },
  ]

  return (
    <nav className={styles.nav}>
      {/* Logo */}
      <div className={styles.logo}>
        <div className={styles.logoIcon}>🏡</div>
        <span>住家<em>.</em>HomeFind</span>
      </div>

      <div className={styles.divider} />

      {/* Nav links */}
      <div className={styles.links}>
        {navItems.map(item => (
          <button
            key={item.key}
            className={`${styles.navBtn} ${page === item.key ? styles.active : ''}`}
            onClick={() => setPage(item.key)}
          >
            <span className={styles.icon}>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>

      {/* Right side */}
      <div className={styles.right}>
        <LanguageSwitcher />
        <button className={styles.signinBtn}>{t.nav_signin}</button>
      </div>
    </nav>
  )
}
