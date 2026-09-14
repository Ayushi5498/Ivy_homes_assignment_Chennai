import { useState, useMemo, useEffect, useRef } from 'react'
import { useListings } from '../hooks/useListings'
import ListingCard from '../components/ListingCard'
import ListingFilters from '../components/ListingFilters'
import styles from './Listings.module.css'

// ── Client-side filtering ────────────────────────────────────────────────────
function applyFilters(listings, filters) {
    const { locality, bedrooms, furnishing, minPrice, maxPrice } = filters
    return listings.filter(r => {
        if (locality && r.locality !== locality) return false
        if (bedrooms && String(r.bedroom) !== String(bedrooms)) return false
        if (furnishing && r.furnishing !== furnishing) return false
        if (minPrice && (r.price ?? 0) < Number(minPrice)) return false
        if (maxPrice && (r.price ?? 0) > Number(maxPrice)) return false
        return true
    })
}

// ── Empty state ──────────────────────────────────────────────────────────────
function EmptyState({ filtered }) {
    return (
        <div className={styles.empty}>
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none"
                stroke="var(--teal-light)" strokeWidth="1.5" aria-hidden="true">
                <path d="M3 9.5 L12 3 L21 9.5 V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z" />
                <path d="M9 21V12h6v9" />
            </svg>
            {filtered
                ? <><h3>No listings match these filters</h3>
                    <p>Try adjusting or clearing your filters.</p></>
                : <><h3>No listings found</h3>
                    <p>There are no listings to display.</p></>
            }
        </div>
    )
}

// ── Loading skeleton ─────────────────────────────────────────────────────────
function SkeletonGrid() {
    return (
        <div className={styles.grid}>
            {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className={styles.skeleton} />
            ))}
        </div>
    )
}

// ── Persist filters in sessionStorage so they survive a page refresh ─────────
const FILTER_KEY = 'ivy_listing_filters'
const DEFAULT_FILTERS = { locality: '', bedrooms: '', furnishing: '', minPrice: '', maxPrice: '' }

function loadFilters() {
    try {
        const saved = sessionStorage.getItem(FILTER_KEY)
        return saved ? { ...DEFAULT_FILTERS, ...JSON.parse(saved) } : DEFAULT_FILTERS
    } catch {
        return DEFAULT_FILTERS
    }
}

function saveFilters(filters) {
    try { sessionStorage.setItem(FILTER_KEY, JSON.stringify(filters)) } catch { /* ignore */ }
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function Listings() {
    // liveListings = all fetched records with is_live === true
    const { liveListings, loading, loadingMore, error, hasMore, loadMore } = useListings()
    const loadMoreRef = useRef(null)

    const [filters, setFilters] = useState(loadFilters)

    // Persist filters whenever they change
    function handleFilterChange(newFilters) {
        setFilters(newFilters)
        saveFilters(newFilters)
    }

    // Sorted unique locality list derived from live data
    const localities = useMemo(() => {
        const set = new Set(liveListings.map(r => r.locality).filter(Boolean))
        return [...set].sort()
    }, [liveListings])

    // Client-side filter applied on top of is_live filter
    const filtered = useMemo(() => applyFilters(liveListings, filters), [liveListings, filters])
    const isFiltered = Object.values(filters).some(v => v !== '')

    // Infinite scroll — observer is created once; loadMore is stable (ref-based)
    useEffect(() => {
        const sentinel = loadMoreRef.current
        if (!sentinel) return
        const obs = new IntersectionObserver(
            entries => { if (entries[0].isIntersecting) loadMore() },
            { rootMargin: '400px' }
        )
        obs.observe(sentinel)
        return () => obs.disconnect()
    }, [loadMore])

    return (
        <main className={styles.page}>
            <div className={styles.inner}>

                {/* Page header */}
                <div className={styles.header}>
                    <h1 className={styles.title}>Listings</h1>
                    <p className={styles.subtitle}>
                        Sale properties across Chennai — browse, filter, and explore.
                    </p>
                </div>

                {/* Filters — show placeholder during load, real controls once data arrives */}
                {liveListings.length > 0 && (
                    <ListingFilters
                        filters={filters}
                        onChange={handleFilterChange}
                        localities={localities}
                        totalShown={filtered.length}
                        totalFetched={liveListings.length}
                    />
                )}
                {loading && liveListings.length === 0 && (
                    <div className={styles.filterSkeleton} aria-hidden="true" />
                )}

                {/* Error banner */}
                {error && (
                    <div className={styles.error} role="alert">
                        Failed to load listings: {error}
                    </div>
                )}

                {/* Shimmer skeleton on first load */}
                {loading && <SkeletonGrid />}

                {/* Card grid */}
                {!loading && filtered.length > 0 && (
                    <div className={styles.grid}>
                        {filtered.map(listing => (
                            <ListingCard key={listing.listing_id} listing={listing} />
                        ))}
                    </div>
                )}

                {/* Empty state */}
                {!loading && !error && liveListings.length > 0 && filtered.length === 0 && (
                    <EmptyState filtered={isFiltered} />
                )}

                {/* Infinite scroll sentinel — only active when not filtering
                    (no point fetching more when user is browsing a filtered view) */}
                {!isFiltered && <div ref={loadMoreRef} className={styles.sentinel} />}

                {/* Spinner shown while loading subsequent pages */}
                {loadingMore && (
                    <div className={styles.loadingMore}>
                        <span className={styles.spinner} aria-label="Loading more listings" />
                        Loading more listings…
                    </div>
                )}

                {/* End-of-list message */}
                {!loading && !loadingMore && !hasMore && liveListings.length > 0 && !isFiltered && (
                    <p className={styles.allLoaded}>
                        All <strong>{liveListings.length}</strong> live listings loaded.
                    </p>
                )}

            </div>
        </main>
    )
}
