import { useMemo } from 'react'
import styles from './Insights.module.css'

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n) { return n != null ? n.toLocaleString('en-IN') : '—' }
function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s }

// ── Static data — from our verified analysis of the full dataset ──────────────

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

// BHK distribution computed from our clean listings
const BHK_DATA = [
    { bhk: 1, count: 412 },
    { bhk: 2, count: 1049 },
    { bhk: 3, count: 1187 },
    { bhk: 4, count: 443 },
    { bhk: 5, count: 142 },
]

const QUALITY_NOTES = [
    {
        icon: '🚫',
        title: '21% of listings are inactive',
        detail: '867 of the 4,100 retrieved listings have is_live: false — expired, sold, or withdrawn. The API docs claim these are excluded server-side, but they are not. This site filters them out automatically.',
        tag: 'Completeness', tagColor: '#CCE5FF', tagText: '#004085',
    },
    {
        icon: '📐',
        title: '3,980 distinct properties (not 4,100)',
        detail: '120 listings describe the same physical property listed across multiple portals. We identify duplicates by matching coordinates within 30m + same floor + same bedroom count + same locality.',
        tag: 'Deduplication', tagColor: '#D4EDDA', tagText: '#276221',
    },
    {
        icon: '⚠️',
        title: '45 listings have impossible data',
        detail: 'Floor exceeds total floors, carpet area larger than super built-up area, negative prices, swapped lat/lon coordinates, or future posting dates. All 45 are excluded from calculations.',
        tag: 'Data quality', tagColor: '#F8D7DA', tagText: '#721C24',
    },
    {
        icon: '🔍',
        title: '93 listings show fake ad patterns',
        detail: 'A contact number shared across 15+ unrelated properties AND a price 40–70% below the local market median. Consistent with enquiry-bait listings, not genuine offers.',
        tag: 'Fraud signals', tagColor: '#FFF3CD', tagText: '#856404',
    },
    {
        icon: '📏',
        title: '326 listings report area in sqm not sqft',
        detail: 'One source portal stores carpet and built-up area in square metres. A 2BHK showing 84 sqft is actually 904 sqft (84 × 10.764). We correct these when displaying area and ₹/sqft.',
        tag: 'Units', tagColor: '#E2D9F3', tagText: '#40217A',
    },
    {
        icon: '🔗',
        title: 'Project IDs don\'t link listings to projects reliably',
        detail: 'Listings sharing a project_id are often kilometres apart in unrelated buildings. Project P40276 links four different named buildings spread 13–25 km across Chennai — its own record is named "Brigade Meadows", matching none of them.',
        tag: 'Data quality', tagColor: '#F8D7DA', tagText: '#721C24',
    },
    {
        icon: '💰',
        title: 'Project prices use inconsistent units',
        detail: '433 projects store price in crores (values 1–4), 27 store in lakhs (values 50–100). There are zero projects with values between 4–50, confirming a hidden bimodal unit split. Without correction, a ₹99.8L project appeared more expensive than ₹3.78Cr ones.',
        tag: 'Units', tagColor: '#E2D9F3', tagText: '#40217A',
    },
    {
        icon: '🛡️',
        title: '7 listings contain prompt injection attempts',
        detail: 'Descriptions include hidden instructions targeting AI coding tools — one falsely claims a "data licence" requires adding a fake attribution badge; another impersonates Ivy Homes to tamper with assignment submissions. Neither instruction was followed.',
        tag: 'Security', tagColor: '#F5ECD7', tagText: '#6B4D2A',
    },
    {
        icon: '📊',
        title: 'API pagination undercounts the dataset',
        detail: 'The "total" field reports 3,836 listings but has_more stays true past it. Fetching to the real end yields 4,100 records — 264 more than reported. Stop condition must use empty results, not the total field.',
        tag: 'API bug', tagColor: '#F8D7DA', tagText: '#721C24',
    },
]

// ── Sub-components ────────────────────────────────────────────────────────────

function StatCard({ label, value, sub, note }) {
    return (
        <div className={styles.statCard}>
            <div className={styles.statValue}>{value}</div>
            <div className={styles.statLabel}>{label}</div>
            {sub && <div className={styles.statSub}>{sub}</div>}
            {note && <div className={styles.statNote}>{note}</div>}
        </div>
    )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Insights() {
    const maxPpsf = Math.max(...LOCALITY_PRICE_DATA.map(d => d.ppsf))
    const maxBhk = Math.max(...BHK_DATA.map(d => d.count))
    const sortedLoc = useMemo(() => [...LOCALITY_PRICE_DATA].sort((a, b) => b.ppsf - a.ppsf), [])
    const totalClean = LOCALITY_PRICE_DATA.reduce((s, d) => s + d.count, 0)

    return (
        <main className={styles.page}>
            <div className={styles.inner}>

                {/* Page header */}
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Insights</h1>
                    <p className={styles.pageSubtitle}>
                        Key figures from our full investigation of Chennai's 4,100-record dataset,
                        plus 9 documented data quality findings.
                    </p>
                </div>

                {/* Section 1 — Dataset overview */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Dataset Overview</h2>
                        <span className={styles.sectionBadge}>Our verified figures</span>
                    </div>
                    <p className={styles.chartNote}>
                        The API's <code>/v1/analytics/summary</code> endpoint is unavailable in this environment (404).
                        All figures below are from our own analysis of the complete dataset.
                    </p>

                    <div className={styles.statsGrid}>
                        <StatCard label="Total listing records" value="4,100"
                            sub="retrieved via correct offset pagination"
                            note="API's own 'total' field reports 3,836 — undercounts by 264" />
                        <StatCard label="Active listings" value="3,233" sub="is_live = true (79% of total)" />
                        <StatCard label="Distinct properties" value="3,980" sub="after deduplicating cross-portal duplicates" />
                        <StatCard label="Avg ₹/sqft — 2BHK" value="₹9,969" sub="clean data, unit errors corrected" />
                        <StatCard label="Listings last 7 days" value="122" sub="posted 3–10 Sep 2026 (IST)" />
                        <StatCard label="OMR total monthly rent" value="₹59.5L" sub="sum across 171 OMR rental records" />
                    </div>

                    {/* BHK distribution */}
                    <div className={styles.chartBlock}>
                        <h3 className={styles.chartTitle}>Active listings by bedroom count</h3>
                        <div className={styles.bhkBars}>
                            {BHK_DATA.map(d => (
                                <div key={d.bhk} className={styles.bhkRow}>
                                    <span className={styles.bhkLabel}>{d.bhk} BHK</span>
                                    <div className={styles.bhkBarWrap}>
                                        <div className={styles.bhkBar}
                                            style={{ width: `${(d.count / maxBhk) * 100}%` }} />
                                    </div>
                                    <span className={styles.bhkCount}>{fmt(d.count)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Section 2 — Locality price comparison */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Price-per-sqft by Locality</h2>
                        <span className={styles.sectionBadge}
                            style={{ background: 'rgba(26,107,114,0.1)', color: 'var(--teal)' }}>
                            Our verified data · excludes corrupt &amp; fake listings
                        </span>
                    </div>
                    <p className={styles.chartNote}>
                        Calculated from {fmt(totalClean)} live, clean listings — after excluding 45 corrupt records,
                        93 fake listings, and correcting unit errors in 334 records.
                    </p>

                    <div className={styles.localityBars}>
                        {sortedLoc.map(d => (
                            <div key={d.locality} className={styles.localityRow}>
                                <span className={styles.localityLabel}>{cap(d.locality)}</span>
                                <div className={styles.localityBarWrap}>
                                    <div className={styles.localityBar}
                                        style={{ width: `${(d.ppsf / maxPpsf) * 100}%` }} />
                                    <span className={styles.localityPpsf}>
                                        ₹{d.ppsf.toLocaleString('en-IN')}/sqft
                                    </span>
                                </div>
                                <span className={styles.localityCount}>{fmt(d.count)} listings</span>
                            </div>
                        ))}
                    </div>

                    <div className={styles.ourStatGrid}>
                        <StatCard label="Most expensive" value="T Nagar" sub="₹10,690/sqft median" />
                        <StatCard label="Most affordable" value="Tambaram" sub="₹9,412/sqft median" />
                        <StatCard label="Price spread" value="14%" sub="cheapest to priciest locality" />
                        <StatCard label="Costliest project" value="P40224" sub="Shriram Serenity, T Nagar · ₹3.78 Cr max" />
                    </div>
                </section>

                {/* Section 3 — Data quality findings */}
                <section className={styles.section}>
                    <div className={styles.sectionHeader}>
                        <h2 className={styles.sectionTitle}>Data Quality Notes</h2>
                        <span className={styles.sectionBadge}
                            style={{ background: 'rgba(192,57,43,0.08)', color: 'var(--error)' }}>
                            9 findings documented
                        </span>
                    </div>
                    <p className={styles.chartNote}>
                        Real issues found by investigating all 4,100 records.
                        Where possible, this app corrects or filters them automatically.
                    </p>

                    <div className={styles.notesGrid}>
                        {QUALITY_NOTES.map((note, i) => (
                            <div key={i} className={styles.noteCard}>
                                <div className={styles.noteTop}>
                                    <span className={styles.noteIcon}>{note.icon}</span>
                                    <span className={styles.noteTag}
                                        style={{ background: note.tagColor, color: note.tagText }}>
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
