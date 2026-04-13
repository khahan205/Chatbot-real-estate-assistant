import { useState } from 'react'
import { useLang } from '../context/LangContext'
import { BG_GRADIENTS } from '../data/properties'
import styles from './PropertyCard.module.css'

export default function PropertyCard({ prop, onAskBot }) {
  const { lang, t } = useLang()
  const [fav, setFav] = useState(false)

  const name = lang === 'en' ? prop.name_en
             : lang === 'vi' ? prop.name_vi
             : prop.name_ja

  const formatPrice = () => {
    if (prop.type === 'rent') {
      const suffix = t.rent_suffix
      const man = Math.round(prop.price / 10000)
      return <>{`¥${man}万`}<span className={styles.priceSub}>{suffix}</span></>
    }
    if (prop.price >= 100_000_000) return `¥${(prop.price / 100_000_000).toFixed(1)}億`
    return `¥${Math.round(prop.price / 10000)}万`
  }

  const badgeLabel = prop.type === 'sale' ? t.type_sale
                   : prop.type === 'rent' ? t.type_rent
                   : t.type_apt
  const badgeClass = prop.type === 'sale' ? styles.bSale
                   : prop.type === 'rent' ? styles.bRent
                   : styles.bApt

  const bedsLabel = lang === 'ja'
    ? `${prop.beds}LDK`
    : `${prop.beds}${t.beds_suffix}`

  return (
    <div className={styles.card} onClick={() => onAskBot(prop)}>
      {/* Image area */}
      <div className={styles.imgWrap} style={{ background: BG_GRADIENTS[prop.bg] }}>
        <span className={styles.emoji}>{prop.emoji}</span>
        <div className={styles.overlay} />

        <div className={styles.badges}>
          <span className={`${styles.badge} ${badgeClass}`}>{badgeLabel}</span>
          {prop.tags.includes('new') && <span className={`${styles.badge} ${styles.bNew}`}>New</span>}
          {prop.tags.includes('hot') && <span className={`${styles.badge} ${styles.bHot}`}>🔥 Hot</span>}
        </div>

        <button
          className={`${styles.fav} ${fav ? styles.favActive : ''}`}
          onClick={(e) => { e.stopPropagation(); setFav(f => !f) }}
        >
          {fav ? '❤️' : '🤍'}
        </button>
      </div>

      {/* Body */}
      <div className={styles.body}>
        <div className={styles.price}>{formatPrice()}</div>
        <div className={styles.name}>{name}</div>
        <div className={styles.loc}>
          <span className={styles.locDot} />
          {prop.loc}
        </div>
        <div className={styles.meta}>
          <span>🛏 {bedsLabel}</span>
          <span>🚿 {prop.baths}{t.bath_suffix}</span>
          <span>📐 {prop.sqm}㎡</span>
          <span>🏗 {prop.built}年</span>
        </div>
      </div>
    </div>
  )
}
