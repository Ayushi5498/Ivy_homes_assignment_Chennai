/**
 * Reusable page shell: title, subtitle, filter bar slot, card grid, infinite
 * scroll sentinel, load-more spinner, empty state, skeleton, end-of-list message.
 */
import { useEffect, useRef } from 'react'
import styles from './PageShell.module.css'

function SkeletonGrid({ count = 8 }) {
    return (
        <div className={styles.grid}>
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className={styles.skeleton} />
            ))}
        </div>
    )
}

function EmptyState({ filtered, noun = 'results' }) {
    return (
        <div className={styles.empty}>
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none"
                stroke="var(--teal-light)" strokeWidth="1.4" aria-hidden="true">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            {filtered
                ? <><h3>No {noun} match these filters</h3><p>Try adjusting or clearing your filters.</p></>
                : <><h3>No {noun} found</h3><p>Nothing to display right now.</p></>
            }
        </div>
    )
}

export default function PageShell({
    title, subtitle,
    filterBar,          // ReactNode — the filter controls
    cards,              // array of items (already filtered)
    loading, loadingMore, hasMore, loadMore,
    error,
    isFiltered,
    totalFetched,
    noun = 'records',
    renderCard,         // (item, index) => ReactNode
}) {
    const sentinelRef = useRef(null)

    useEffect(() => {
        const el = sentinelRef.current
        if (!el) return
        const obs = new IntersectionObserver(
            entries => { if (entries[0].isIntersecting) loadMore() },
            { rootMargin: '400px' }
        )
        obs.observe(el)
        return () => obs.disconnect()
    }, [loadMore])

    return (
        <main className={styles.page}>
            <div className={styles.inner}>
                <div className={styles.header}>
                    <h1 className={styles.title}>{title}</h1>
                    {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
                </div>

                {/* Filter skeleton while loading first batch */}
                {loading && totalFetched === 0 && (
                    <div className={styles.filterSkeleton} aria-hidden="true" />
                )}

                {/* Real filter bar once we have data */}
                {!loading && totalFetched > 0 && filterBar}

                {error && (
                    <div className={styles.error} role="alert">
                        Failed to load {noun}: {error}
                    </div>
                )}

                {loading && <SkeletonGrid />}

                {!loading && cards.length > 0 && (
                    <div className={styles.grid}>
                        {cards.map((item, i) => renderCard(item, i))}
                    </div>
                )}

                {!loading && !error && totalFetched > 0 && cards.length === 0 && (
                    <EmptyState filtered={isFiltered} noun={noun} />
                )}

                {!isFiltered && <div ref={sentinelRef} className={styles.sentinel} />}

                {loadingMore && (
                    <div className={styles.loadingMore}>
                        <span className={styles.spinner} aria-label={`Loading more ${noun}`} />
                        Loading more…
                    </div>
                )}

                {!loading && !loadingMore && !hasMore && totalFetched > 0 && !isFiltered && (
                    <p className={styles.allLoaded}>
                        All <strong>{totalFetched}</strong> {noun} loaded.
                    </p>
                )}
            </div>
        </main>
    )
}
