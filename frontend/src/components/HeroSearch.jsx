import { useState } from 'react'
import { useLang } from '../context/LangContext'
import styles from './HeroSearch.module.css'

const STATS = [
  { num: '12K+', keyLabel: 'stat_listings' },
  { num: '47',   keyLabel: 'stat_pref'     },
  { num: '98%',  keyLabel: 'stat_sat'      },
]

export default function HeroSearch() {
  const { t } = useLang()
  const [activeTab, setActiveTab] = useState(0)
  const tabs = [t.tab_buy, t.tab_rent, t.tab_new]

  return (
    <div className={styles.wrapper}>
      <div className={styles.left}>
        <div className={styles.badge}>✦ {t.hero_badge}</div>
        <h2 className={styles.heading}>
          {t.hero_h2.split('\n').map((line, i) => <span key={i}>{line}<br /></span>)}
        </h2>
        <p className={styles.sub}>{t.hero_sub}</p>

        {/* Search box */}
        <div className={styles.searchBox}>
          <div className={styles.tabs}>
            {tabs.map((tab, i) => (
              <button
                key={i}
                className={`${styles.tab} ${activeTab === i ? styles.tabActive : ''}`}
                onClick={() => setActiveTab(i)}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className={styles.fields}>
            <div className={styles.field}>
              <label>{t.sf_area}</label>
              <input type="text" placeholder={t.sf_area_ph} />
            </div>
            <div className={styles.field}>
              <label>{t.sf_type}</label>
              <select>
                <option>{t.sf_all_type}</option>
                <option>マンション</option>
                <option>一戸建て</option>
                <option>ワンルーム</option>
                <option>土地</option>
              </select>
            </div>
          </div>
          <button className={styles.searchBtn}>{t.search_go}</button>
        </div>
      </div>

      {/* Stats */}
      <div className={styles.stats}>
        {STATS.map((s, i) => (
          <div key={i} className={styles.stat}>
            <div className={styles.statNum}>{s.num}</div>
            <div className={styles.statLabel}>{t[s.keyLabel]}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
