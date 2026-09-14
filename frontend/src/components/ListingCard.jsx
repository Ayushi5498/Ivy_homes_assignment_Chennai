import { Link } from 'react-router-dom'
import styles from './ListingCard.module.css'

// Deterministic color from a string (for the placeholder thumbnail)
function colorFromString(str = '') {
    const palette = [
        '#C8673A', '#1A6B72', '#2D3561', '#8B6914',
        '#7B4F3A', '#2A8F99', '#5B4B8A', '#4A7C59',
    ]
    let hash = 0
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash)
    return palette[Math.abs(hash) % palette.length]
}

function formatPrice(p) {
    if (!p) return '—'
    if (p >= 10_000_000) return `₹${(p / 10_000_000).toFixed(2)} Cr`
    if (p >= 100_000) return `₹${(p / 100_000).toFixed(1)} L`
    return `₹${p.toLocaleString('en-IN')}`
}

const FURNISH_BADGE = {
    'fully-furnished': { label: 'Furnished', bg: '#D4EDDA', color: '#276221' },
    'semi-furnished': { label: 'Semi-furnished', bg: '#FFF3CD', color: '#856404' },
    'unfurnished': { label: 'Unfurnished', bg: '#F5ECD7', color: '#6B4D2A' },
}

export default function ListingCard({ listing }) {
    const {
        listing_id, apartment_name, locality, bedroom, bathroom,
        price, carpet_area, furnishing, property_type, floor, posted_by,
    } = listing

    const thumbColor = colorFromString(apartment_name)
    const badge = FURNISH_BADGE[furnishing] ?? { label: furnishing, bg: '#eee', color: '#555' }

    return (
        <Link to={`/listings/${listing_id}`} className={styles.card}>
            {/* Thumbnail placeholder */}
            <div className={styles.thumb} style={{ background: thumbColor }} aria-hidden="true">
                <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 38 L6 22 L24 8 L42 22 L42 38 Z"
                        fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.4)"
                        strokeWidth="1.5" strokeLinejoin="round" />
                    <rect x="18" y="28" width="12" height="10"
                        fill="rgba(255,255,255,0.25)" rx="1" />
                    <rect x="28" y="22" width="7" height="7"
                        fill="rgba(255,255,255,0.2)" rx="1" />
                </svg>
                <span className={styles.propType}>{property_type}</span>
            </div>

            <div className={styles.body}>
                <div className={styles.topRow}>
                    <span className={styles.locality}>{locality}</span>
                    <span
                        className={styles.furnishBadge}
                        style={{ background: badge.bg, color: badge.color }}
                    >
                        {badge.label}
                    </span>
                </div>

                <h3 className={styles.name}>{apartment_name || 'Unnamed property'}</h3>

                <div className={styles.specs}>
                    <span title="Bedrooms">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2" aria-hidden="true">
                            <path d="M3 9v6M21 9v6M3 13h18M3 7h18M7 7v2M17 7v2" />
                        </svg>
                        {bedroom ?? '—'} BHK
                    </span>
                    <span title="Bathrooms">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" strokeWidth="2" aria-hidden="true">
                            <path d="M4 12h16v4a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-4z" />
                            <path d="M4 12V6a2 2 0 0 1 2-2h1v8" />
                        </svg>
                        {bathroom ?? '—'} Bath
                    </span>
                    {carpet_area && (
                        <span title="Carpet area">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                <rect x="3" y="3" width="18" height="18" rx="1" />
                            </svg>
                            {carpet_area} sqft
                        </span>
                    )}
                    {floor > 0 && (
                        <span title="Floor">Floor {floor}</span>
                    )}
                </div>

                <div className={styles.footer}>
                    <span className={styles.price}>{formatPrice(price)}</span>
                    {posted_by && (
                        <span className={styles.postedBy}>{posted_by}</span>
                    )}
                </div>
            </div>
        </Link>
    )
}
