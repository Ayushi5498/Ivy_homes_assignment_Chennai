import { useState, useMemo } from 'react'
import { fetchProjectsPage, normProjectPrice } from '../api/client'
import { usePaginatedFetch } from '../hooks/usePaginatedFetch'
import PageShell from '../components/PageShell'
import styles from './Projects.module.css'

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatPrice(rupees) {
    if (!rupees) return null
    if (rupees >= 1_00_00_000) return `₹${(rupees / 1_00_00_000).toFixed(2)} Cr`
    if (rupees >= 1_00_000) return `₹${(rupees / 1_00_000).toFixed(1)}L`
    return `₹${rupees.toLocaleString('en-IN')}`
}

function formatPriceRange(minRaw, maxRaw) {
    const minR = normProjectPrice(minRaw)
    const maxR = normProjectPrice(maxRaw)
    if (!minR && !maxR) return null
    if (!minR) return formatPrice(maxR)
    if (!maxR) return formatPrice(minR)
    return `${formatPrice(minR)} – ${formatPrice(maxR)}`
}

function formatDate(d) {
    if (!d) return null
    try {
        return new Date(d).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
    } catch { return d }
}

function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }

function colorFromString(str = '') {
    const palette = ['#2D3561', '#1A6B72', '#8B6914', '#7B4F3A', '#5B4B8A', '#4A7C59', '#2A8F99']
    let h = 0
    for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h)
    return palette[Math.abs(h) % palette.length]
}

const STATUS_STYLE = {
    'ready to move': { bg: '#D4EDDA', color: '#276221' },
    'new launch': { bg: '#CCE5FF', color: '#004085' },
    'under construction': { bg: '#FFF3CD', color: '#856404' },
}

// ── Project card ──────────────────────────────────────────────────────────────

function ProjectCard({ item }) {
    const {
        project_id, apartment_name, developer_name, locality,
        project_status, total_units, price_min, price_max,
        possession_date, amenities, total_floors,
    } = item

    const priceRange = formatPriceRange(price_min, price_max)
    const statusStyle = STATUS_STYLE[project_status] ?? { bg: '#eee', color: '#555' }
    const amenityList = Array.isArray(amenities) ? amenities.slice(0, 4) : []

    return (
        <div className={styles.card}>
            {/* Header band */}
            <div className={styles.band} style={{ background: colorFromString(apartment_name) }}>
                <div className={styles.bandText}>
                    <span className={styles.devName}>{developer_name}</span>
                    <span className={styles.projId}>{project_id}</span>
                </div>
                {project_status && (
                    <span className={styles.statusBadge}
                        style={{ background: statusStyle.bg, color: statusStyle.color }}>
                        {cap(project_status)}
                    </span>
                )}
            </div>

            <div className={styles.body}>
                <div className={styles.locality}>{locality}</div>
                <h3 className={styles.name}>{apartment_name || 'Unnamed project'}</h3>

                <div className={styles.meta}>
                    {total_units && <span>{total_units.toLocaleString('en-IN')} units</span>}
                    {total_floors && <span>{total_floors} floors</span>}
                    {possession_date && <span>Possession {formatDate(possession_date)}</span>}
                </div>

                {/* Amenity tags */}
                {amenityList.length > 0 && (
                    <div className={styles.amenities}>
                        {amenityList.map(a => (
                            <span key={a} className={styles.amenityTag}>{a}</span>
                        ))}
                        {amenities.length > 4 && (
                            <span className={styles.amenityMore}>+{amenities.length - 4}</span>
                        )}
                    </div>
                )}

                <div className={styles.footer}>
                    {priceRange
                        ? <span className={styles.price}>{priceRange}</span>
                        : <span className={styles.priceNA}>Price on request</span>
                    }
                </div>
            </div>
        </div>
    )
}

// ── Filter bar ────────────────────────────────────────────────────────────────

const FILTER_KEY = 'ivy_project_filters'
const DEFAULT_FILTERS = { locality: '', status: '' }

function loadFilters() {
    try { const s = sessionStorage.getItem(FILTER_KEY); return s ? { ...DEFAULT_FILTERS, ...JSON.parse(s) } : DEFAULT_FILTERS } catch { return DEFAULT_FILTERS }
}

function ProjectFilters({ filters, onChange, localities, statuses, totalShown, totalFetched }) {
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
                    <label>Status</label>
                    <select value={filters.status} onChange={e => set('status', e.target.value)}>
                        <option value="">All statuses</option>
                        {statuses.map(s => <option key={s} value={s}>{cap(s)}</option>)}
                    </select>
                </div>
                {dirty && <button className={styles.resetBtn} onClick={reset}>Clear filters</button>}
            </div>
            <p className={styles.count}>
                {totalShown === totalFetched
                    ? <><strong>{totalFetched}</strong> projects fetched so far</>
                    : <><strong>{totalShown}</strong> of <strong>{totalFetched}</strong> projects match filters</>
                }
            </p>
        </div>
    )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Projects() {
    const { items, loading, loadingMore, error, hasMore, loadMore } =
        usePaginatedFetch(fetchProjectsPage)

    const [filters, setFilters] = useState(loadFilters)

    const localities = useMemo(() =>
        [...new Set(items.map(r => r.locality).filter(Boolean))].sort()
        , [items])

    const statuses = useMemo(() =>
        [...new Set(items.map(r => r.project_status).filter(Boolean))].sort()
        , [items])

    const filtered = useMemo(() => {
        return items.filter(r => {
            if (filters.locality && r.locality !== filters.locality) return false
            if (filters.status && r.project_status !== filters.status) return false
            return true
        })
    }, [items, filters])

    const isFiltered = Object.values(filters).some(v => v !== '')

    return (
        <PageShell
            title="Projects"
            subtitle="New developments and builder projects across Chennai."
            filterBar={
                <ProjectFilters
                    filters={filters}
                    onChange={setFilters}
                    localities={localities}
                    statuses={statuses}
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
            noun="projects"
            renderCard={item => <ProjectCard key={item.project_id} item={item} />}
        />
    )
}
