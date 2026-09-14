import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchListingById } from '../api/client'
import { useAuth } from '../context/AuthContext'
import styles from './ListingDetail.module.css'

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatPrice(p) {
    if (!p) return '—'
    if (p >= 10_000_000) return `₹${(p / 10_000_000).toFixed(2)} Cr`
    if (p >= 100_000) return `₹${(p / 100_000).toFixed(1)} L`
    return `₹${p.toLocaleString('en-IN')}`
}

function formatDate(iso) {
    if (!iso) return '—'
    try {
        return new Date(iso).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'long', year: 'numeric',
        })
    } catch { return iso }
}

function capitalize(s) {
    if (!s) return '—'
    return s.charAt(0).toUpperCase() + s.slice(1)
}

// ── Sub-components ────────────────────────────────────────────────────────────

function SpecItem({ icon, label, value }) {
    if (value === null || value === undefined || value === '') return null
    return (
        <div className={styles.specItem}>
            <span className={styles.specIcon} aria-hidden="true">{icon}</span>
            <div>
                <div className={styles.specLabel}>{label}</div>
                <div className={styles.specValue}>{value}</div>
            </div>
        </div>
    )
}

function Tag({ children, variant = 'default' }) {
    return <span className={`${styles.tag} ${styles[variant]}`}>{children}</span>
}

// ── Coloured placeholder thumbnail (same logic as ListingCard) ────────────────
function colorFromString(str = '') {
    const palette = ['#C8673A', '#1A6B72', '#2D3561', '#8B6914', '#7B4F3A', '#2A8F99', '#5B4B8A', '#4A7C59']
    let hash = 0
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash)
    return palette[Math.abs(hash) % palette.length]
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function ListingDetail() {
    const { id } = useParams()
    const { accessToken } = useAuth()

    const [listing, setListing] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)   // null | 'NOT_FOUND' | string
    const [favourite, setFavourite] = useState(false)

    useEffect(() => {
        if (!accessToken || !id) return
        setLoading(true)
        setError(null)
        fetchListingById(accessToken, id)
            .then(data => setListing(data))
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [id, accessToken])

    // ── Loading ────────────────────────────────────────────────────────────
    if (loading) return (
        <main className={styles.page}>
            <div className={styles.inner}>
                <div className={styles.skeletonHero} />
                <div className={styles.skeletonBody}>
                    {[220, 160, 300, 180].map((w, i) => (
                        <div key={i} className={styles.skeletonLine} style={{ width: w }} />
                    ))}
                </div>
            </div>
        </main>
    )

    // ── Not found ──────────────────────────────────────────────────────────
    if (error === 'NOT_FOUND') return (
        <main className={styles.page}>
            <div className={`${styles.inner} ${styles.centred}`}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none"
                    stroke="var(--teal-light)" strokeWidth="1.2" aria-hidden="true">
                    <circle cx="12" cy="12" r="10" /><path d="M12 8v4m0 4h.01" />
                </svg>
                <h2 className={styles.notFoundTitle}>Listing not found</h2>
                <p className={styles.notFoundSub}>
                    The listing <code>{id}</code> doesn't exist or has been removed.
                </p>
                <Link to="/listings" className={styles.backBtn}>← Back to Listings</Link>
            </div>
        </main>
    )

    // ── Generic error ──────────────────────────────────────────────────────
    if (error) return (
        <main className={styles.page}>
            <div className={`${styles.inner} ${styles.centred}`}>
                <h2>Something went wrong</h2>
                <p className={styles.notFoundSub}>{error}</p>
                <Link to="/listings" className={styles.backBtn}>← Back to Listings</Link>
            </div>
        </main>
    )

    if (!listing) return null

    const {
        listing_id, apartment_name, locality, property_type, furnishing,
        price, bedroom, bathroom, balcony, floor, total_floors,
        carpet_area, super_built_up_area, facing_direction, covered_parking,
        description, posted_by, posted_by_name, posted_by_contact,
        is_verified, is_live, posted_at, website, listing_url,
    } = listing

    const thumbColor = colorFromString(apartment_name)

    return (
        <main className={styles.page}>
            <div className={styles.inner}>

                {/* Back link */}
                <Link to="/listings" className={styles.backLink}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                        <path d="M19 12H5M12 5l-7 7 7 7" />
                    </svg>
                    Back to Listings
                </Link>

                {/* ── Not-live banner ── */}
                {!is_live && (
                    <div className={styles.notLiveBanner} role="alert">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2" aria-hidden="true">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 8v4m0 4h.01" />
                        </svg>
                        This listing is no longer active — it may have been sold, rented or withdrawn.
                    </div>
                )}

                {/* ── Hero ── */}
                <div className={styles.hero} style={{ background: thumbColor }}>
                    <svg viewBox="0 0 80 60" fill="none" xmlns="http://www.w3.org/2000/svg"
                        className={styles.heroIcon} aria-hidden="true">
                        <path d="M10 52 L10 28 L40 8 L70 28 L70 52 Z"
                            fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.45)"
                            strokeWidth="1.5" strokeLinejoin="round" />
                        <rect x="28" y="36" width="24" height="16"
                            fill="rgba(255,255,255,0.2)" rx="1.5" />
                        <rect x="46" y="24" width="14" height="12"
                            fill="rgba(255,255,255,0.15)" rx="1" />
                    </svg>
                    <div className={styles.heroOverlay}>
                        <div className={styles.heroMeta}>
                            <span className={styles.heroId}>{listing_id}</span>
                            {is_verified && (
                                <span className={styles.verifiedBadge}>
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="2.5" aria-hidden="true">
                                        <polyline points="20 6 9 17 4 12" />
                                    </svg>
                                    Verified
                                </span>
                            )}
                        </div>
                        <div className={styles.heroPrice}>{formatPrice(price)}</div>
                    </div>
                </div>

                {/* ── Main content grid ── */}
                <div className={styles.contentGrid}>

                    {/* Left / main column */}
                    <div className={styles.main}>

                        {/* Title + tags */}
                        <div className={styles.titleBlock}>
                            <h1 className={styles.title}>{apartment_name || 'Unnamed property'}</h1>
                            <div className={styles.tags}>
                                {locality && <Tag variant="locality">{capitalize(locality)}</Tag>}
                                {property_type && <Tag>{capitalize(property_type)}</Tag>}
                                {furnishing && <Tag variant="furnish">{capitalize(furnishing)}</Tag>}
                            </div>
                        </div>

                        {/* Spec grid */}
                        <section className={styles.section}>
                            <h2 className={styles.sectionTitle}>Property details</h2>
                            <div className={styles.specGrid}>
                                <SpecItem icon="🛏" label="Bedrooms" value={bedroom != null ? `${bedroom} BHK` : null} />
                                <SpecItem icon="🚿" label="Bathrooms" value={bathroom} />
                                <SpecItem icon="🌿" label="Balconies" value={balcony} />
                                <SpecItem icon="🏢" label="Floor" value={floor != null && total_floors ? `${floor} / ${total_floors}` : floor} />
                                <SpecItem icon="📐" label="Carpet area" value={carpet_area ? `${carpet_area} sqft` : null} />
                                <SpecItem icon="📏" label="Super built-up" value={super_built_up_area ? `${super_built_up_area} sqft` : null} />
                                <SpecItem icon="🧭" label="Facing" value={capitalize(facing_direction)} />
                                <SpecItem icon="🚗" label="Covered parking" value={covered_parking != null ? (covered_parking ? `${covered_parking} slot` : 'None') : null} />
                            </div>
                        </section>

                        {/* Description */}
                        {description && (
                            <section className={styles.section}>
                                <h2 className={styles.sectionTitle}>Description</h2>
                                <p className={styles.description}>{description}</p>
                            </section>
                        )}

                        {/* Source link */}
                        {listing_url && (
                            <section className={styles.section}>
                                <h2 className={styles.sectionTitle}>Source</h2>
                                <a href={listing_url} target="_blank" rel="noopener noreferrer"
                                    className={styles.sourceLink}>
                                    View on {website ? website.charAt(0).toUpperCase() + website.slice(1) : 'original site'}
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                                        <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                                    </svg>
                                </a>
                            </section>
                        )}
                    </div>

                    {/* Right / sidebar */}
                    <aside className={styles.sidebar}>

                        {/* Price card */}
                        <div className={styles.priceCard}>
                            <div className={styles.priceLabel}>Sale price</div>
                            <div className={styles.priceBig}>{formatPrice(price)}</div>
                            {carpet_area && price && (
                                <div className={styles.pricePsf}>
                                    ₹{Math.round(price / carpet_area).toLocaleString('en-IN')} / sqft
                                </div>
                            )}

                            {/* Favourite button */}
                            <button
                                className={`${styles.favBtn} ${favourite ? styles.favActive : ''}`}
                                onClick={() => setFavourite(f => !f)}
                                aria-label={favourite ? 'Remove from favourites' : 'Save to favourites'}
                            >
                                <svg width="18" height="18" viewBox="0 0 24 24"
                                    fill={favourite ? 'currentColor' : 'none'}
                                    stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                                </svg>
                                {favourite ? 'Saved' : 'Save to Favourites'}
                            </button>
                        </div>

                        {/* Seller card */}
                        <div className={styles.sellerCard}>
                            <h3 className={styles.sellerTitle}>Listed by</h3>
                            <div className={styles.sellerName}>
                                {posted_by_name || 'Unknown'}
                            </div>
                            <div className={styles.sellerType}>
                                {capitalize(posted_by)}
                            </div>
                            {posted_by_contact && (
                                <a href={`tel:${posted_by_contact}`}
                                    className={styles.contactBtn}>
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13 19.79 19.79 0 0 1 1.62 4.4 2 2 0 0 1 3.6 2.22h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 9.91a16 16 0 0 0 6.18 6.18l.95-.95a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 17v-.08z" />
                                    </svg>
                                    {posted_by_contact}
                                </a>
                            )}
                            <div className={styles.postedAt}>
                                Posted {formatDate(posted_at)}
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </main>
    )
}
