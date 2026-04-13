import { useState, useMemo } from 'react'
import { useLang } from '../context/LangContext'
import FilterBar from '../components/FilterBar'
import PropertyCard from '../components/PropertyCard'
import properties from '../data/properties'
import styles from './HotPage.module.css'

const SORT_OPTIONS = [
  { value: 'default',    labelKey: 'sort_feat'  },
  { value: 'price-asc',  labelKey: 'sort_pasc'  },
  { value: 'price-desc', labelKey: 'sort_pdesc' },
  { value: 'newest',     labelKey: 'sort_new'   },
]

const DEFAULT_FILTERS = { type: 'all', price: 'all', beds: 'all', area: 'all' }

export default function HotPage({ onAskBot }) {
  const { t } = useLang()
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [sort, setSort]       = useState('default')

  const filtered = useMemo(() => {
    let list = properties.filter(p => {
      if (filters.type !== 'all' && p.type !== filters.type) return false
      if (filters.area !== 'all' && p.area !== filters.area) return false
      if (filters.price !== 'all') {
        if (filters.price === 'low'  && p.price >= 50_000_000) return false
        if (filters.price === 'mid'  && (p.price < 50_000_000 || p.price > 100_000_000)) return false
        if (filters.price === 'high' && p.price < 100_000_000) return false
      }
      if (filters.beds !== 'all') {
        if (filters.beds === '1' && p.beds !== 1) return false
        if (filters.beds === '2' && p.beds !== 2) return false
        if (filters.beds === '3' && p.beds < 3)   return false
      }
      return true
    })

    if (sort === 'price-asc')  list = [...list].sort((a, b) => a.price - b.price)
    if (sort === 'price-desc') list = [...list].sort((a, b) => b.price - a.price)
    if (sort === 'newest')     list = [...list].sort((a, b) => b.id - a.id)
    return list
  }, [filters, sort])

  return (
    <div>
      <FilterBar filters={filters} setFilters={setFilters} count={filtered.length} />

      <div className={styles.wrapper}>
        {/* Header row */}
        <div className={styles.headerRow}>
          <div>
            <h1 className={styles.title}>{t.hot_title}</h1>
            <p className={styles.sub}>{t.hot_sub}</p>
          </div>
          <select
            className={styles.sortSelect}
            value={sort}
            onChange={e => setSort(e.target.value)}
          >
            {SORT_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{t[o.labelKey]}</option>
            ))}
          </select>
        </div>

        {/* Grid */}
        {filtered.length > 0 ? (
          <div className={styles.grid}>
            {filtered.map(p => (
              <PropertyCard key={p.id} prop={p} onAskBot={onAskBot} />
            ))}
          </div>
        ) : (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>🔍</div>
            <div className={styles.emptyText}>{t.hot_title}が見つかりません</div>
            <div className={styles.emptySub}>Try adjusting your filters</div>
          </div>
        )}
      </div>
    </div>
  )
}
