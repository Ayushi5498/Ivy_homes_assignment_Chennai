import { useFavourites } from '../context/FavouritesContext'
import { Link } from 'react-router-dom'
import styles from './Favourites.module.css'

function formatPrice(p) {
    if (!p) return '—'
    if (p >= 10_000_000) return `₹${(p / 10_000_000).toFixed(2)} Cr`
    if (p >= 100_000) return `₹${(p / 100_000).toFixed(1)} L`
    return `₹${p.toLocaleString('en-IN')}`
}

function colorFromString(str = '') {
    const palette = ['#C8673A', '#1A6B72', '#2D3561', '#8B6914', '#7B4F3A', '#2A8F99', '#5B4B8A', '#4A7C59']
    let hash = 0
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash)
    return palette[Math.abs(hash) % palette.length]
}

export default function Favourites() {
    const { savedIds, loading, toggleSaved } = useFavourites()

    // savedIds is a Set of listing_id strings.
    // The full listing objects come from GET /v1/saved via the context,
    // but we store only IDs in the Set. We need the full objects for display —
    // they're available via context's raw data. Let's expose them properly.
    // For now, use the FavouritesContext which already fetched full objects.
    return <FavouritesInner />
}

// Inner component that uses the full saved listings data from context
function FavouritesInner() {
    const { savedListings, loading, toggleSaved } = useFavourites()

    if (loading) return (
        <main className={styles.page}>
            <div className={styles.inner}>
                <h1 className={styles.title}>Favourites</h1>
                <div className={styles.grid}>
                    {[1, 2, 3, 4].map(i => <div key={i} className={styles.skeleton} />)}
                </div>
            </div>
        </main>
    )

    return (
        <main className={styles.page}>
            <div className={styles.inner}>
                <div className={styles.header}>
                    <h1 className={styles.title}>Favourites</h1>
                    <p className={styles.subtitle}>
                        {savedListings.length > 0
                            ? `${savedListings.length} saved listing${savedListings.length !== 1 ? 's' : ''}`
                            : 'No saved listings yet'}
                    </p>
                </div>

                {savedListings.length === 0 ? (
                    <div className={styles.empty}>
                        <svg width="56" height="56" viewBox="0 0 24 24" fill="none"
                            stroke="var(--teal-light)" strokeWidth="1.2" aria-hidden="true">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                        </svg>
                        <h3>Nothing saved yet</h3>
                        <p>Open a listing and click "Save to Favourites" to add it here.</p>
                        <Link to="/listings" className={styles.browseBtn}>Browse Listings</Link>
                    </div>
                ) : (
                    <div className={styles.grid}>
                        {savedListings.map(listing => (
                            <FavouriteCard
                                key={listing.listing_id}
                                listing={listing}
                                onRemove={() => toggleSaved(listing.listing_id)}
                            />
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}

function FavouriteCard({ listing, onRemove }) {
    const {
        listing_id, apartment_name, locality, bedroom,
        bathroom, carpet_area, price, furnishing, property_type,
    } = listing

    return (
        <div className={styles.card}>
            {/* Coloured thumb */}
            <Link to={`/listings/${listing_id}`} className={styles.thumb}
                style={{ background: colorFromString(apartment_name) }}
                aria-label={`View ${apartment_name}`}>
                <svg viewBox="0 0 48 36" fill="none" className={styles.thumbIcon} aria-hidden="true">
                    <path d="M6 33 L6 17 L24 5 L42 17 L42 33 Z"
                        fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
                    <rect x="17" y="22" width="14" height="11" fill="rgba(255,255,255,0.22)" rx="1" />
                </svg>
                <span className={styles.propType}>{property_type}</span>
            </Link>

            <div className={styles.body}>
                <div className={styles.locality}>{locality}</div>
                <Link to={`/listings/${listing_id}`} className={styles.name}>
                    {apartment_name || 'Unnamed property'}
                </Link>
                <div className={styles.specs}>
                    {bedroom != null && <span>{bedroom} BHK</span>}
                    {bathroom != null && <span>{bathroom} Bath</span>}
                    {carpet_area && <span>{carpet_area} sqft</span>}
                </div>
                <div className={styles.footer}>
                    <span className={styles.price}>{formatPrice(price)}</span>
                    {/* Remove button — calls DELETE /v1/saved/{listing_id} */}
                    <button className={styles.removeBtn} onClick={onRemove}
                        aria-label={`Remove ${apartment_name} from favourites`}>
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"
                            stroke="currentColor" strokeWidth="2" aria-hidden="true">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                        </svg>
                        Remove
                    </button>
                </div>
            </div>
        </div>
    )
}
