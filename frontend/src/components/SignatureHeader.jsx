import { useLang } from '../context/LangContext'
import styles from './SignatureHeader.module.css'

function HouseSVG() {
  return (
    <svg width="220" height="220" viewBox="0 0 220 220" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="110" cy="130" r="80" fill="rgba(127,156,120,0.08)" />
      <rect x="55" y="110" width="110" height="85" rx="4"
        fill="rgba(244,241,233,0.08)" stroke="rgba(244,241,233,0.2)" strokeWidth="1.5" />
      <path d="M40 115 L110 50 L180 115"
        stroke="rgba(244,241,233,0.35)" strokeWidth="2" strokeLinejoin="round"
        fill="rgba(127,156,120,0.15)" />
      <line x1="110" y1="50" x2="110" y2="38" stroke="rgba(197,106,82,0.6)" strokeWidth="2.5" />
      <circle cx="110" cy="34" r="5" fill="rgba(197,106,82,0.7)" />
      <rect x="93" y="148" width="34" height="47" rx="3"
        fill="rgba(107,79,58,0.35)" stroke="rgba(244,241,233,0.18)" strokeWidth="1" />
      <circle cx="121" cy="172" r="2.5" fill="rgba(200,169,110,0.7)" />
      <rect x="64" y="122" width="28" height="22" rx="2"
        fill="rgba(127,156,120,0.2)" stroke="rgba(244,241,233,0.2)" strokeWidth="1" />
      <line x1="78" y1="122" x2="78" y2="144" stroke="rgba(244,241,233,0.15)" strokeWidth="1" />
      <line x1="64" y1="133" x2="92" y2="133" stroke="rgba(244,241,233,0.15)" strokeWidth="1" />
      <rect x="128" y="122" width="28" height="22" rx="2"
        fill="rgba(127,156,120,0.2)" stroke="rgba(244,241,233,0.2)" strokeWidth="1" />
      <line x1="142" y1="122" x2="142" y2="144" stroke="rgba(244,241,233,0.15)" strokeWidth="1" />
      <line x1="128" y1="133" x2="156" y2="133" stroke="rgba(244,241,233,0.15)" strokeWidth="1" />
      <line x1="40" y1="195" x2="180" y2="195" stroke="rgba(244,241,233,0.12)" strokeWidth="1.5" />
      <circle cx="32" cy="178" r="14" fill="rgba(127,156,120,0.18)" stroke="rgba(127,156,120,0.3)" strokeWidth="1" />
      <line x1="32" y1="192" x2="32" y2="195" stroke="rgba(107,79,58,0.3)" strokeWidth="2" />
      <circle cx="188" cy="176" r="12" fill="rgba(127,156,120,0.18)" stroke="rgba(127,156,120,0.3)" strokeWidth="1" />
      <line x1="188" y1="188" x2="188" y2="195" stroke="rgba(107,79,58,0.3)" strokeWidth="2" />
    </svg>
  )
}

export default function SignatureHeader() {
  const { t } = useLang()

  return (
    <div className={styles.banner}>
      {/* Decorative circles */}
      <div className={`${styles.decoCircle} ${styles.dc1}`} />
      <div className={`${styles.decoCircle} ${styles.dc2}`} />
      <div className={`${styles.decoCircle} ${styles.dc3}`} />

      {/* Left: text */}
      <div className={`${styles.left} anim-fu delay-1`}>
        <div className={styles.eyebrow}>{t.banner_eyebrow}</div>
        <h1 className={styles.wordmark}>
          Home<em>Find</em>
        </h1>
        <p className={styles.jpLine}>{t.banner_jp}</p>
        <p className={styles.tagline}>
          {t.banner_tagline.split('\n').map((line, i) => (
            <span key={i}>{line}<br /></span>
          ))}
        </p>
      </div>

      {/* Right: SVG house icon */}
      <div className={`${styles.right} anim-fu delay-3`}>
        <HouseSVG />
      </div>

      {/* Arc cutout at bottom */}
      <div className={styles.arc} />
    </div>
  )
}
