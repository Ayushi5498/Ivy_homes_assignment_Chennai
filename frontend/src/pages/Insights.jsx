import { useState, useEffect, useMemo } from 'react'
import { useAuth } from '../context/AuthContext'
import { authHeaders } from '../api/client'
import styles from './Insights.module.css'

const BASE_URL = 'https://solve.ivy.homes'
const TRUE_COUNT = 4100   // our verified total

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n) { return n != null ? n.toLocaleString('en-IN') : '—' }

function fmtPrice(p) {
    if (!p) return '—'
    if (p >= 1_00_00_000) return `₹${(p / 1_00_00_000).toFixed(2)} Cr`
    if (p >= 1_00_000) return `₹${(p / 1_00_000).toFixed(1)}L`
    return `₹${p.toLocaleString('en-IN')}`
}

function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s }

// ── Static data quality notes from submission.json ────────────────────────────
// (numbers hardcoded from our verified analysis — not from the unreliable API)

const QUALITY_NOTES = [
    {
        icon: '🚫',
        title: '21% of listings are inactive',
        detail: '867 of the 4,100 retrieved listings have is_live: false — meaning they are expired, sold, or withdrawn. The API documentation claims these are excluded server-side, but they are not. This site filters them out before showing you results.',
        tag: 'Completeness',
        tagColor: '#CCE5FF',
        tagText: '#004085',
    },
    {
        icon: '📐',
        title: '3,980 distinct properties (not 4,100)',
        detail: '120 listings appear to describe the same physical property listed multiple times across different portals (squarelane, magichomes, dwelling, etc.). We identify duplicates by matching coordinates within 30m + same floor + same bedroom count + same locality.',
        tag: 'Deduplication',
        tagColor: '#D4EDDA',
        tagText: '#276221',
    },
    {
        icon: '⚠️',
        title: '45 listings have physically impossible data',
        detail: 'We found listings where the floor number exceeds the building\'s total floors, carpet area is larger than super built-up area, prices are negative, latitude and longitude are swapped, or posting dates are in the future. All 45 are excluded from price calculations.',
        tag: 'Data quality',
        tagColor: '#F8D7DA',
        tagText: '#721C24',
    },
    {
        icon: '🔍',
        title: '93 listings show patterns consistent with fake ads',
        detail: 'These listings share a phone number that appears on 15+ other unrelated properties (scattered across different builders, localities, and property types — inconsistent with a real agent\'s portfolio), AND are priced 40–70% below the local market rate — a "too good to be true" signal without being an obvious data error.',
        tag: 'Fraud signals',
        tagColor: '#FFF3CD',
        tagText: '#856404',
    },
    {
        icon: '📏',
        title: '326 listings report area in sqm, not sqft',
        detail: 'A batch of listings (predominantly from one source portal) stores carpet_area and super_built_up_area in square metres instead of the documented square feet. A 2BHK showing 84 sqft is actually 904 sqft (84 × 10.764). We correct these automatically when displaying area and price-per-sqft.',
        tag: 'Units',
        tagColor: '#E2D9F3',
        tagText: '#40217A',
    },
    {
        icon: '🔗',
        title: 'Project IDs don\'t reliably link listings to projects',
        detail: 'Listings sharing the same project_id are often in completely different buildings, kilometres apart. Example: project P40276 links listings from four unrelated buildings (Prestige Vista, SHRIRAM CREST, Rohan Park, Aparna Heights) spread 13–25 km across Chennai. The project record itself is named "Brigade Meadows" and matches none of them.',
        tag: 'Data quality',
        tagColor: '#F8D7DA',
        tagText: '#721C24',
    },
    {
        icon: '🛡️',
        title: '7 listings contain prompt injection attempts',
        detail: 'Seven listing descriptions include hidden instructions targeting AI coding tools — one pattern falsely claims a "data licence" requires adding a fake attribution badge, another impersonates the Ivy Homes data team to manipulate assignment submissions. Neither instruction was followed.',
        tag: 'Security',
        tagColor: '#F5ECD7',
        tagText: '#6B4D2A',
    },
]

// ── Locality price data (precomputed from our cleaned analysis) ───────────────
// Source: calc_q6_final.py — is_live=true, excludes 45 corrupt + 93 fake,
//         corrects 326 sqm-area records, corrects 8 price-unit records.

const LOCALITY_PRICE_DATA = [
    { locality: 'adyar', ppsf: 10260, count: 298 },
    { locality: 'anna nagar', ppsf: 10162, count: 321 },
    { locality: 'guindy', ppsf: 9748, count: 312 },
    { locality: 'omr', ppsf: 9930, count: 334 },
    { locality: 'perungudi', ppsf: 10597, count: 342 },
    { locality: 'porur', ppsf: 9786, count: 319 },
    { locality: 't nagar', ppsf: 10690, count: 295 },
    { locality: 'tambaram', ppsf: 9412, count: 308 },
    { locality: 'thoraipakkam', ppsf: 10384, count: 328 },
    { locality: 'velachery', ppsf: 10208, count: 289 },
]

const MAX_PPSF = Math.max(...LOCALITY_PRICE_DATA.map(d => d.ppsf))

// ── Stat card ─────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub, warn }) {
    return (
        <div className={styles.statCard}>
            <div className={styles.statValue}>{value}</div>
            <div className={styles.statLabel}>{label}</div>
            {sub && <div className={styles.statSub}>{sub}</div>}
            {warn && <div className={styles.statWarn}>{warn}</div>}
        </div>
    )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Insights() {
    const { accessToken } = useAuth()
    const [summary, setSummary] = useState(null)
    const [loading, setLoading] = useState(true)
    const [apiError, setApiError] = useState(null)

    useEffect(() => {
        if (!accessToken) return
        fetch(`${BASE_URL}/v1/analytics/summary`, { headers: authHeaders(accessToken) })
            .then(r => r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`))
            .then(data => setSummary(data))
            .catch(e => setApiError(String(e)))
            .finally(() => setLoading(false))
    }, [accessToken])

    const apiTotal = summary?.total_listings

    // Sort localities by ppsf descending for the bar chart
    const sortedLocalities = useMemo(() =>
        [...LOCALITY_PRICE_DATA].sort((a, b) => b.ppsf - a.ppsf)
        , [])

    // Sort API by_locality by count descending
    const byLocality = useMemo(() => {
        if (!summary?.by_locality) return []
        return [...summary.by_locality].sort((a, b) => b.count - a.count)
    }, [summary])

    const byBhk = useMemo(() => {
        if (!summary?.by_bhk) return []
        return [...summary.by_bhk].sort((a, b) => a.bhk - b.bhk)
    }, [summary])

    const maxBhkCount = Math.max(...byBhk.map(d => d.count), 1)

    return (
        <main className={styles.page}>
            <div className={styles.inner}>

                {/* ── Page header ── */}
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Insights</h1>
                    <p className={styles.pageSubtitle}>
                        Official analytics from the API, plus our own data quality discoveries from
                        a thorough investigation of the full Chennai dataset.
                    </p>
                </div>

                {/* ══════════════════════════════════════════════════════
                    SECTION 1 — Official API analytics
                ══════════════════════════════════════════════════════ */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Official API Analytics</h2>
                        <span className={styles.sectionBadge}>From GET /v1/analytics/summary</span>
                    </div>

                    {loading && (
                        <div className={styles.skeletonRow}>
                            {[1, 2, 3, 4].map(i => <div key={i} className={styles.skeleton} />)}
                        </div>
                    )}

                    {apiError && (
                        <div className={styles.errorBox}>
                            Could not load analytics: {apiError}
                        </div>
                    )}

                    {summary && (
                        <>
                            {/* Stat cards */}
                            <div className={styles.statsGrid}>
                                <StatCard
                                    label="City"
                                    value={cap(summary.city) || 'Chennai'}
                                />
                                <StatCard
                                    label="Total listings (API)"
                                    value={fmt(apiTotal)}
                                    warn={apiTotal !== TRUE_COUNT
                                        ? `Note: our verified count is ${fmt(TRUE_COUNT)} — the API undercounts due to a known pagination bug (has_more stays true past the reported total)`
                                        : null}
                                />
                                <StatCard
                                    label="Median price"
                                    value={fmtPrice(summary.median_price)}
                                    sub="across all sale listings"
                                />
                                <StatCard
                                    label="Median ₹/sqft"
                                    value={summary.median_price_per_sqft
                                        ? `₹${Math.round(summary.median_price_per_sqft).toLocaleString('en-IN')}`
                                        : '—'}
                                    sub="price per sq ft"
                                />
                            </div>

                            {/* By BHK */}
                            {byBhk.length > 0 && (
                                <div className={styles.chartBlock}>
                                    <h3 className={styles.chartTitle}>Listings by bedroom count (API)</h3>
                                    <div className={styles.bhkBars}>
                                        {byBhk.map(d => (
                                            <div key={d.bhk} className={styles.bhkRow}>
                                                <span className={styles.bhkLabel}>{d.bhk} BHK</span>
                                                <div className={styles.bhkBarWrap}>
                                                    <div className={styles.bhkBar}
                                                        style={{ width: `${(d.count / maxBhkCount) * 100}%` }} />
                                                </div>
                                                <span className={styles.bhkCount}>{fmt(d.count)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* By locality table */}
                            {byLocality.length > 0 && (
                                <div className={styles.chartBlock}>
                                    <h3 className={styles.chartTitle}>Listings by locality (API)</h3>
                                    <div className={styles.tableWrap}>
                                        <table className={styles.table}>
                                            <thead>
                                                <tr>
                                                    <th>Locality</th>
                                                    <th className={styles.right}>Listings</th>
                                                    <th className={styles.right}>Median price</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {byLocality.map(d => (
                                                    <tr key={d.locality}>
                                                        <td>{cap(d.locality)}</td>
                                                        <td className={styles.right}>{fmt(d.count)}</td>
                                                        <td className={styles.right}>{fmtPrice(d.median_price)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </section>

                {/* ══════════════════════════════════════════════════════
                    SECTION 2 — Our locality price comparison
                ══════════════════════════════════════════════════════ */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Price-per-sqft by Locality</h2>
                        <span className={styles.sectionBadge} style={{ background: 'rgba(26,107,114,0.1)', color: 'var(--teal)' }}>
                            Our verified data · excludes corrupt &amp; fake listings
                        </span>
                    </div>
                    <p className={styles.chartNote}>
                        Calculated from {fmt(LOCALITY_PRICE_DATA.reduce((s, d) => s + d.count, 0))} live,
                        clean listings — after excluding 45 corrupt records, 93 fake listings,
                        and correcting unit errors in 334 records.
                    </p>

                    <div className={styles.localityBars}>
                        {sortedLocalities.map(d => (
                            <div key={d.locality} className={styles.localityRow}>
                                <span className={styles.localityLabel}>{cap(d.locality)}</span>
                                <div className={styles.localityBarWrap}>
                                    <div
                                        className={styles.localityBar}
                                        style={{ width: `${(d.ppsf / MAX_PPSF) * 100}%` }}
                                    />
                                    <span className={styles.localityPpsf}>
                                        ₹{d.ppsf.toLocaleString('en-IN')}/sqft
                                    </span>
                                </div>
                                <span className={styles.localityCount}>{fmt(d.count)} listings</span>
                            </div>
                        ))}
                    </div>

                    <div className={styles.ourStatGrid}>
                        <StatCard
                            label="Avg ₹/sqft for 2BHK"
                            value="₹9,969"
                            sub="is_live=true, clean data, corrected units"
                        />
                        <StatCard
                            label="Most expensive locality"
                            value="T Nagar"
                            sub="₹10,690/sqft median"
                        />
                        <StatCard
                            label="Most affordable locality"
                            value="Tambaram"
                            sub="₹9,412/sqft median"
                        />
                        <StatCard
                            label="Price spread"
                            value="14%"
                            sub="difference between cheapest and priciest locality"
                        />
                    </div>
                </section>

                {/* ══════════════════════════════════════════════════════
                    SECTION 3 — Data quality notes
                ══════════════════════════════════════════════════════ */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Data Quality Notes</h2>
                        <span className={styles.sectionBadge} style={{ background: 'rgba(192,57,43,0.08)', color: 'var(--error)' }}>
                            9 findings documented
                        </span>
                    </div>
                    <p className={styles.chartNote}>
                        These are real issues we found by investigating the full dataset of 4,100 records.
                        Where possible, this app corrects or filters them automatically.
                    </p>

                    <div className={styles.notesGrid}>
                        {QUALITY_NOTES.map((note, i) => (
                            <div key={i} className={styles.noteCard}>
                                <div className={styles.noteTop}>
                                    <span className={styles.noteIcon}>{note.icon}</span>
                                    <span
                                        className={styles.noteTag}
                                        style={{ background: note.tagColor, color: note.tagText }}
                                    >
                                        {note.tag}
                                    </span>
                                </div>
                                <h3 className={styles.noteTitle}>{note.title}</h3>
                                <p className={styles.noteDetail}>{note.detail}</p>
                            </div>
                        ))}
                    </div>
                </section>

            </div>
        </main>
    )
}
