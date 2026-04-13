import { useLang } from '../context/LangContext'
import styles from './FilterBar.module.css'

const TYPE_FILTERS = [
  { value: 'all',  labelKey: 'f_all'  },
  { value: 'sale', labelKey: 'f_sale' },
  { value: 'rent', labelKey: 'f_rent' },
  { value: 'apt',  labelKey: 'f_apt'  },
]

export default function FilterBar({ filters, setFilters, count }) {
  const { t } = useLang()

  const set = (key, val) => setFilters(prev => ({ ...prev, [key]: val }))

  return (
    <div className={styles.bar}>
      <div className={styles.inner}>
        <span className={styles.label}>{t.filter_label}</span>

        {/* Type pills */}
        {TYPE_FILTERS.map(f => (
          <button
            key={f.value}
            className={`${styles.pill} ${filters.type === f.value ? styles.pillActive : ''}`}
            onClick={() => set('type', f.value)}
          >
            {t[f.labelKey]}
          </button>
        ))}

        <div className={styles.sep} />

        {/* Price */}
        <select
          className={styles.select}
          value={filters.price}
          onChange={e => set('price', e.target.value)}
        >
          <option value="all">{t.f_any_price}</option>
          <option value="low">〜 ¥5,000万</option>
          <option value="mid">¥5,000万〜¥1億</option>
          <option value="high">¥1億以上</option>
        </select>

        {/* Beds */}
        <select
          className={styles.select}
          value={filters.beds}
          onChange={e => set('beds', e.target.value)}
        >
          <option value="all">{t.f_any_bed}</option>
          <option value="1">1K / 1R</option>
          <option value="2">2LDK</option>
          <option value="3">3LDK以上</option>
        </select>

        {/* Area */}
        <select
          className={styles.select}
          value={filters.area}
          onChange={e => set('area', e.target.value)}
        >
          <option value="all">{t.f_any_area}</option>
          <option value="tokyo">東京</option>
          <option value="osaka">大阪</option>
          <option value="kyoto">京都</option>
          <option value="other">その他</option>
        </select>

        <div className={styles.count}>
          <strong>{count}</strong> {t.f_results}
        </div>
      </div>
    </div>
  )
}
