import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchListingsPage } from '../api/client'
import { useAuth } from '../context/AuthContext'

const PAGE_SIZE = 50

export function useListings() {
    const { accessToken } = useAuth()

    // Keep a ref to the latest token so callbacks never go stale
    const tokenRef = useRef(accessToken)
    useEffect(() => { tokenRef.current = accessToken }, [accessToken])

    // All LIVE listings fetched so far (is_live === true only)
    const [liveListings, setLiveListings] = useState([])
    const [loading, setLoading] = useState(false)
    const [loadingMore, setLoadingMore] = useState(false)
    const [error, setError] = useState(null)
    const [hasMore, setHasMore] = useState(true)

    // Use refs for pagination state so callbacks always see the latest values
    const offsetRef = useRef(0)
    const hasMoreRef = useRef(true)
    const isFetching = useRef(false)   // prevents concurrent fetches

    // ── Core fetch function ────────────────────────────────────────────────
    const loadPage = useCallback(async (isFirst = false) => {
        // Guards against concurrent calls and fetching past the end
        if (isFetching.current) return
        if (!hasMoreRef.current && !isFirst) return
        if (!tokenRef.current) return

        isFetching.current = true

        if (isFirst) {
            setLoading(true)
            setError(null)
            setLiveListings([])
            offsetRef.current = 0
            hasMoreRef.current = true
            setHasMore(true)
        } else {
            setLoadingMore(true)
        }

        try {
            const data = await fetchListingsPage(
                tokenRef.current,
                offsetRef.current,
                PAGE_SIZE
            )
            const results = data.results ?? []

            // Advance offset by ACTUAL results returned (not PAGE_SIZE)
            // — mirrors the fix in our Python script
            offsetRef.current += results.length

            // Stop condition: has_more is false OR empty batch — ignore "total"
            const more = data.has_more === true && results.length > 0
            hasMoreRef.current = more
            setHasMore(more)

            // Filter to live listings only before storing
            const live = results.filter(r => r.is_live === true)
            setLiveListings(prev => isFirst ? live : [...prev, ...live])

        } catch (err) {
            setError(err.message)
            hasMoreRef.current = false
            setHasMore(false)
        } finally {
            setLoading(false)
            setLoadingMore(false)
            isFetching.current = false
        }
    }, []) // no deps — uses refs so it's always fresh

    // ── Initial load on mount / token change ──────────────────────────────
    useEffect(() => {
        if (!accessToken) return
        loadPage(true)
    }, [accessToken, loadPage])

    // ── Public loadMore — safe to call from scroll handler ────────────────
    const loadMore = useCallback(() => {
        if (!isFetching.current && hasMoreRef.current) {
            loadPage(false)
        }
    }, [loadPage])

    return { liveListings, loading, loadingMore, error, hasMore, loadMore }
}
