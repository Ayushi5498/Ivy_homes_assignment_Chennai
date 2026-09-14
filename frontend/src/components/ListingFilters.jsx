import styles from './ListingFilters.module.css'

const FURNISHING_OPTIONS = ['', 'unfurnished', 'semi-furnished', 'fully-furnished']
const BEDROOM_OPTIONS = ['', '1', '2', '3', '4', '5']

export default function ListingFilters({ filters, onChange, localities, totalShown, totalFetched }) {
    function set(key, value) {
        onChange({ ...filters, [key]: value })
    }

    function reset() {
        onChange({ locality: '', bedrooms: '', minPrice: '', maxPrice: '', furnishing: '' })
        try { sessionStorage.removeItem('ivy_listing_filters') } catch { /* ignore */ }
    }

    const isDirty = Object.values(filters).some(v => v !== '')

    return (
        <div className={styles.bar}>
            <div className={styles.controls}>
                {/* Locality */}
                <div className={styles.field}>
                    <label htmlFor="f-locality">Locality</label>
                    <select id="f-locality" value={filters.locality}
                        onChange={e => set('locality', e.target.value)}>
                        <option value="">All localities</option>
                        {localities.map(l => (
                            <option key={l} value={l}>{l}</option>
                        ))}
                    </select>
                </div>

                {/* Bedrooms */}
                <div className={styles.field}>
                    <label htmlFor="f-bed">Bedrooms</label>
                    <select id="f-bed" value={filters.bedrooms}
                        onChange={e => set('bedrooms', e.target.value)}>
                        <option value="">Any</option>
                        {BEDROOM_OPTIONS.filter(Boolean).map(n => (
                            <option key={n} value={n}>{n} BHK</option>
                        ))}
                    </select>
                </div>

                {/* Furnishing */}
                <div className={styles.field}>
                    <label htmlFor="f-furnish">Furnishing</label>
                    <select id="f-furnish" value={filters.furnishing}
                        onChange={e => set('furnishing', e.target.value)}>
                        <option value="">Any</option>
                        {FURNISHING_OPTIONS.filter(Boolean).map(f => (
                            <option key={f} value={f}>{f}</option>
                        ))}
                    </select>
                </div>

                {/* Min price */}
                <div className={styles.field}>
                    <label htmlFor="f-minprice">Min price (₹)</label>
                    <input id="f-minprice" type="number" min="0" step="100000"
                        placeholder="e.g. 5000000"
                        value={filters.minPrice}
                        onChange={e => set('minPrice', e.target.value)} />
                </div>

                {/* Max price */}
                <div className={styles.field}>
                    <label htmlFor="f-maxprice">Max price (₹)</label>
                    <input id="f-maxprice" type="number" min="0" step="100000"
                        placeholder="e.g. 20000000"
                        value={filters.maxPrice}
                        onChange={e => set('maxPrice', e.target.value)} />
                </div>

                {isDirty && (
                    <button className={styles.resetBtn} onClick={reset} type="button">
                        Clear filters
                    </button>
                )}
            </div>

            <p className={styles.count}>
                {totalShown === totalFetched
                    ? <><strong>{totalFetched}</strong> live listings fetched so far</>
                    : <><strong>{totalShown}</strong> of <strong>{totalFetched}</strong> live listings match filters</>
                }
            </p>
        </div>
    )
}
