import { useLang } from '../context/LangContext'
import SignatureHeader from '../components/SignatureHeader'
import HeroSearch from '../components/HeroSearch'
import PropertyCard from '../components/PropertyCard'
import properties from '../data/properties'
import styles from './HomePage.module.css'

const HOT_AREAS = [
  { name: '東京都', en: 'Tokyo Metropolitan', emoji: '🏯', countKey: 'area_count_tokyo', span: true,  bg: 'linear-gradient(160deg,#1a2a1a,#0a1a0a)' },
  { name: '大阪府', en: 'Osaka Prefecture',   emoji: '🏮', countKey: 'area_count_osaka', span: false, bg: 'linear-gradient(160deg,#2a1a0a,#1a0a00)' },
  { name: '京都府', en: 'Kyoto Prefecture',   emoji: '⛩️', countKey: 'area_count_kyoto', span: false, bg: 'linear-gradient(160deg,#0a1a2a,#000a1a)' },
  { name: '福岡県', en: 'Fukuoka Prefecture', emoji: '🌸', countKey: 'area_count_fuk',   span: false, bg: 'linear-gradient(160deg,#1a2a0a,#0a1a00)' },
  { name: '北海道', en: 'Hokkaido',           emoji: '❄️', countKey: 'area_count_hok',   span: false, bg: 'linear-gradient(160deg,#0a1a2a,#001020)' },
]

const MAP_PINS = [
  { top: '28%', left: '22%', emoji: '🏠', color: 'var(--accent)',  label: '渋谷区 · ¥6,800万', sub: '3LDK · 82㎡' },
  { top: '48%', left: '48%', emoji: '🏢', color: 'var(--matcha)', label: '新宿区 · ¥4,200万', sub: '2LDK · 65㎡' },
  { top: '18%', left: '63%', emoji: '🏯', color: 'var(--accent)',  label: '港区 · ¥12,800万',  sub: '4LDK · 145㎡' },
  { top: '63%', left: '38%', emoji: '🌿', color: 'var(--cedar)',   label: '目黒区 · ¥3,800万',  sub: '2LDK · 58㎡' },
  { top: '52%', left: '70%', emoji: '🏠', color: 'var(--accent)',  label: '世田谷 · ¥5,200万',  sub: '3LDK · 91㎡' },
]

const FEATURES = [
  { icon: '🤖', titleKey: 'feat1_t', jpKey: 'feat1_jp', descKey: 'feat1_d' },
  { icon: '🗺️', titleKey: 'feat2_t', jpKey: 'feat2_jp', descKey: 'feat2_d' },
  { icon: '間',  titleKey: 'feat3_t', jpKey: 'feat3_jp', descKey: 'feat3_d' },
  { icon: '🌐', titleKey: 'feat4_t', jpKey: 'feat4_jp', descKey: 'feat4_d' },
]

const FOOTER_COLS = [
  { titleKey: 'footer_buy',  links: ['fl_new_condo','fl_resale','fl_house','fl_land','fl_akiya'] },
  { titleKey: 'footer_rent', links: ['fl_apt','fl_share','fl_short','fl_furn'] },
  { titleKey: 'footer_co',   links: ['fl_about','fl_agent','fl_blog','fl_contact','fl_privacy'] },
]

export default function HomePage({ setPage, onAskBot }) {
  const { t } = useLang()

  const featured = properties.filter(p => p.tags.length > 0 || p.id <= 4).slice(0, 6)

  return (
    <div>
      {/* 1. Signature header banner */}
      <SignatureHeader />

      {/* 2. Hero search */}
      <HeroSearch />

      {/* 3. Hot areas */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <div className={styles.kicker}>{t.areas_kicker}</div>
          <h2 className={styles.sectionTitle}>{t.areas_title}</h2>
        </div>
        <div className={styles.areasGrid}>
          {HOT_AREAS.map((area, i) => (
            <div
              key={i}
              className={`${styles.areaCard} ${area.span ? styles.areaSpan : ''}`}
            >
              <div className={styles.areaBg} style={{ background: area.bg }}>
                <span className={styles.areaEmoji}>{area.emoji}</span>
              </div>
              <div className={styles.areaOverlay} />
              <div className={styles.areaInfo}>
                <div className={styles.areaName}>{area.name}</div>
                <div className={styles.areaEn}>{area.en}</div>
                <span className={styles.areaCount}>{t[area.countKey]}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Featured properties */}
      <section className={styles.sectionNoTop}>
        <div className={styles.sectionHeader}>
          <div className={styles.kicker}>{t.feat_kicker}</div>
          <h2 className={styles.sectionTitle}>{t.feat_title}</h2>
        </div>
        <div className={styles.propsGrid}>
          {featured.map(p => (
            <PropertyCard key={p.id} prop={p} onAskBot={onAskBot} />
          ))}
        </div>
        <div className={styles.seeAll}>
          <button className={styles.seeAllBtn} onClick={() => setPage('hot')}>
            {t.see_all_btn}
          </button>
        </div>
      </section>

      {/* 5. Map section */}
      <div className={styles.mapSection}>
        <div className={styles.mapInner}>
          <div className={styles.mapText}>
            <div className={styles.mapKicker}>{t.map_kicker}</div>
            <div className={styles.mapTitle}>Map Search</div>
            <div className={styles.mapTitleJp}>{t.map_title_jp}</div>
            <p className={styles.mapDesc}>{t.map_desc}</p>
            <button className={styles.mapBtn} onClick={() => setPage('map')}>
              {t.map_btn}
            </button>
          </div>

          <div className={styles.mapVisual}>
            {/* Grid pattern */}
            <div className={styles.mapGrid} />

            {/* Pins */}
            {MAP_PINS.map((pin, i) => (
              <div key={i} className={styles.pinWrap} style={{ top: pin.top, left: pin.left }}>
                <div className={styles.pin} style={{ background: pin.color }}>
                  <span className={styles.pinEmoji}>{pin.emoji}</span>
                </div>
                <div className={styles.pinPopup}>
                  {pin.label}<br /><small>{pin.sub}</small>
                </div>
              </div>
            ))}

            {/* Stations */}
            <div className={styles.stations}>
              {['🚉 渋谷', '🚉 新宿', '🚉 池袋', '🚉 銀座'].map(s => (
                <span key={s} className={styles.station}>{s}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 6. Features strip */}
      <div className={styles.featuresStrip}>
        <div className={styles.featuresInner}>
          {FEATURES.map((f, i) => (
            <div key={i} className={styles.featureItem}>
              <span className={styles.featureIcon}>{f.icon}</span>
              <div className={styles.featureTitle}>{t[f.titleKey]}</div>
              <div className={styles.featureJp}>{t[f.jpKey]}</div>
              <div className={styles.featureDesc}>{t[f.descKey]}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 7. Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div>
            <div className={styles.footerLogo}>住家<em>.</em>HomeFind</div>
            <p className={styles.footerDesc}>{t.footer_desc}</p>
            <p className={styles.footerDescJp}>Premium bilingual real estate for Japan</p>
          </div>
          {FOOTER_COLS.map((col, i) => (
            <div key={i}>
              <div className={styles.footColTitle}>{t[col.titleKey]}</div>
              {col.links.map(lk => (
                <a key={lk} className={styles.footLink}>{t[lk]}</a>
              ))}
            </div>
          ))}
        </div>
        <div className={styles.footerBottom}>
          <div>{t.footer_copy}</div>
          <div className={styles.footerBottomJp}>© 2025 住家 HomeFind. All rights reserved.</div>
        </div>
      </footer>
    </div>
  )
}
