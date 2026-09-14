import { useState, useMemo } from 'react'
import { fetchRentalsPage } from '../api/client'
import { usePaginatedFetch } from '../hooks/usePaginatedFetch'
import PageShell from '../components/PageShell'
import styles from './Rentals.module.css'

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatRent(p) {
    if (!p) return '—'
    if (p >= 100_000) return `₹${(p / 100_000).toFixed(1)}L/mo`
    return `₹${p.toLocaleString('en-IN')}/mo`
}

function formatDeposit(p) {
    if (!p) return null
    if (p >= 100_000) return `₹${(p / 100_000).toFixed(1)}L deposit`
    return `₹${p.toLocaleString('en-IN')} deposit`
}

function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '—' }

function colorFromString(str = '') {
    const palette = ['#2A8F99', '#1A6B72', '#4A7C59', '#5B4B8A', '#8B6914', '#2D3561']
    let h = 0
    for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h)
    return palette[Math.abs(h) % palette.length]
}

const FURNISH_BADGE = {
    'fully-furnished': { bg: '#D4EDDA', color: '#276221', label: 'Furnished' },
    'semi-furnished': { bg: '#FFF3CD', color: '#856404', label: 'Semi-furnished' },
    'unfurnished': { bg: '#F5ECD7', color: '#6B4D2A', label: 'Unfurnished' },
}

// ── Rental card ───────────────────────────────────────────────────────────────

function RentalCard({ item }) {
    const {
        listing_id, apartment_name, locality, bedroom, bathroom,
        price, deposit, carpet_area, furnishing, property_type,
    } = item
    const badge = FURNISH_BADGE[furnishing] ?? { bg: '#eee', color: '#555', label: furnishing }

    return (
        <div className={styles.card}>
            <div className={styles.thumb} style={{ background: colorFromString(apartment_name) }}>
                <svg viewBox="0 0 48 36" fill="none" className={styles.thumbIcon} aria-hidden="true">
                    <path d="M4 28L4 16L24 4L44 16L44 28Z"
                        fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
                    <rect x="15" y="18" width="18" height="10" fill="rgba(255,255,255,0.2)" rx="1" />
                </svg>
                <span className={styles.propBadge}>{property_type}</span>
            </div>

            <div className={styles.body}>
                <div className={styles.topRow}>
                    <span className={styles.locality}>{locality}</span>
                    <span className={styles.furnish}
                        style={{ background: badge.bg, color: badge.color }}>
                        {badge.label}
                    </span>
                </div>

                <h3 className={styles.name}>{apartment_name || 'Unnamed property'}</h3>

                <div className={styles.specs}>
                    {bedroom != null && <span>{bedroom} BHK</span>}
                    {bathroom != null && <span>{bathroom} Bath</span>}
                    {carpet_area && <span>{carpet_area} sqft</span>}
                </div>

                <div className={styles.footer}>
                    <div>
                        <div className={styles.rent}>{formatRent(price)}</div>
                        {deposit > 0 && (
                            <div className={styles.deposit}>{formatDeposit(deposit)}</div>
                        )}
                    </div>
                    <span className={styles.idTag}>{listing_id}</span>
                </div>
            </div>
        </div>
    )
}

// ── Filter bar ────────────────────────────────────────────────────────────────

const FILTER_KEY = 'ivy_rental_filters'
const DEFAULT_FILTERS = { locality: '', bedrooms: '', furnishing: '' }

function loadFilters() {
    try { const s = sessionStorage.getItem(FILTER_KEY); return s ? { ...DEFAULT_FILTERS, ...JSON.parse(s) } : DEFAULT_FILTERS } catch { return DEFAULT_FILTERS }
}

function RentalFilters({ filters, onChange, localities, totalShown, totalFetched }) {
    function set(k, v) {
        const next = { ...filters, [k]: v }
        onChange(next)
        try { sessionStorage.setItem(FILTER_KEY, JSON.stringify(next)) } catch { }
    }
    function reset() {
        onChange(DEFAULT_FILTERS)
        try { sessionStorage.removeItem(FILTER_KEY) } catch { }
    }
    const dirty = Object.values(filters).some(v => v !== '')

    return (
        <div className={styles.filterBar}>
            <div className={styles.controls}>
                <div className={styles.field}>
                    <label>Locality</label>
                    <select value={filters.locality} onChange={e => set('locality', e.target.value)}>
                        <option value="">All localities</option>
                        {localities.map(l => <option key={l} value={l}>{l}</option>)}
                    </select>
                </div>
                <div className={styles.field}>
                    <label>Bedrooms</label>
                    <select value={filters.bedrooms} onChange={e => set('bedrooms', e.target.value)}>
                        <option value="">Any</option>
                        {['1', '2', '3', '4', '5'].map(n => <option key={n} value={n}>{n} BHK</option>)}
                    </select>
                </div>
                <div className={styles.field}>
                    <label>Furnishing</label>
                    <select value={filters.furnishing} onChange={e => set('furnishing', e.target.value)}>
                        <option value="">Any</option>
                        <option value="unfurnished">Unfurnished</option>
                        <option value="semi-furnished">Semi-furnished</option>
                        <option value="fully-furnished">Fully furnished</option>
                    </select>
                </div>
                {dirty && <button className={styles.resetBtn} onClick={reset}>Clear filters</button>}
            </div>
            <p className={styles.count}>
                {totalShown === totalFetched
                    ? <><strong>{totalFetched}</strong> rentals fetched so far</>
                    : <><strong>{totalShown}</strong> of <strong>{totalFetched}</strong> rentals match filters</>
                }
            </p>
        </div>
    )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Rentals() {
    const { items, loading, loadingMore, error, hasMore, loadMore } =
        usePaginatedFetch(fetchRentalsPage)

    const [filters, setFilters] = useState(loadFilters)

    const localities = useMemo(() => {
        return [...new Set(items.map(r => r.locality).filter(Boolean))].sort()
    }, [items])

    const filtered = useMemo(() => {
        return items.filter(r => {
            if (filters.locality && r.locality !== filters.locality) return false
            if (filters.bedrooms && String(r.bedroom) !== String(filters.bedrooms)) return false
            if (filters.furnishing && r.furnishing !== filters.furnishing) return false
            return true
        })
    }, [items, filters])

    const isFiltered = Object.values(filters).some(v => v !== '')

    return (
        <PageShell
            title="Rentals"
            subtitle="Rental properties across Chennai — find your next home."
            filterBar={
                <RentalFilters
                    filters={filters}
                    onChange={setFilters}
                    localities={localities}
                    totalShown={filtered.length}
                    totalFetched={items.length}
                />
            }
            cards={filtered}
            loading={loading}
            loadingMore={loadingMore}
            hasMore={hasMore}
            loadMore={loadMore}
            error={error}
            isFiltered={isFiltered}
            totalFetched={items.length}
            noun="rentals"
            renderCard={item => <RentalCard key={item.listing_id} item={item} />}
        />
    )
}
