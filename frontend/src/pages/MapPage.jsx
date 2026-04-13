import { useLang } from '../context/LangContext'
import styles from './MapPage.module.css'

const PINS = [
  { top: '30%', left: '25%', emoji: '🏠', color: 'var(--accent)',  label: '渋谷区 · ¥6,800万', sub: '3LDK' },
  { top: '55%', left: '55%', emoji: '🏢', color: 'var(--matcha)', label: '新宿区 · ¥4,200万', sub: '2LDK' },
  { top: '22%', left: '68%', emoji: '🏯', color: 'var(--accent)',  label: '港区 · ¥12,800万',  sub: '4LDK' },
  { top: '65%', left: '35%', emoji: '🌿', color: 'var(--cedar)',   label: '目黒区 · ¥3,800万',  sub: '2LDK' },
  { top: '40%', left: '72%', emoji: '🏡', color: 'var(--accent)',  label: '世田谷 · ¥5,200万',  sub: '3LDK' },
]

export default function MapPage() {
  const { t } = useLang()

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>{t.map_page_title}</h1>

      <div className={styles.mapContainer}>
        <div className={styles.grid} />

        {/* Coming soon overlay */}
        <div className={styles.comingSoon}>
          <div className={styles.comingIcon}>🗺️</div>
          <div className={styles.comingText}>{t.map_coming}</div>
          <div className={styles.comingSub}>Map feature coming soon</div>
        </div>

        {/* Sample pins */}
        {PINS.map((pin, i) => (
          <div key={i} className={styles.pinWrap} style={{ top: pin.top, left: pin.left }}>
            <div className={styles.pin} style={{ background: pin.color }}>
              <span className={styles.pinEmoji}>{pin.emoji}</span>
            </div>
            <div className={styles.popup}>
              {pin.label}<br /><small>{pin.sub}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
