import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'

const PAGE_SIZE = 50

/**
 * Generic offset-based pagination hook.
 * @param {(token, offset, limit) => Promise<{results, has_more}>} fetchFn
 * @param {(item) => boolean} [filterFn]  optional post-fetch filter (e.g. is_live)
 */
export function usePaginatedFetch(fetchFn, filterFn) {
    const { accessToken } = useAuth()
    const tokenRef = useRef(accessToken)
    useEffect(() => { tokenRef.current = accessToken }, [accessToken])

    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(false)
    const [loadingMore, setLoadingMore] = useState(false)
    const [error, setError] = useState(null)
    const [hasMore, setHasMore] = useState(true)

    const offsetRef = useRef(0)
    const hasMoreRef = useRef(true)
    const isFetching = useRef(false)

    const loadPage = useCallback(async (isFirst = false) => {
        if (isFetching.current) return
        if (!hasMoreRef.current && !isFirst) return
        if (!tokenRef.current) return

        isFetching.current = true

        if (isFirst) {
            setLoading(true)
            setError(null)
            setItems([])
            offsetRef.current = 0
            hasMoreRef.current = true
            setHasMore(true)
        } else {
            setLoadingMore(true)
        }

        try {
            const data = await fetchFn(tokenRef.current, offsetRef.current, PAGE_SIZE)
            const results = data.results ?? []

            offsetRef.current += results.length   // advance by ACTUAL count

            const more = data.has_more === true && results.length > 0
            hasMoreRef.current = more
            setHasMore(more)

            const batch = filterFn ? results.filter(filterFn) : results
            setItems(prev => isFirst ? batch : [...prev, ...batch])
        } catch (err) {
            setError(err.message)
            hasMoreRef.current = false
            setHasMore(false)
        } finally {
            setLoading(false)
            setLoadingMore(false)
            isFetching.current = false
        }
    }, [fetchFn, filterFn])

    useEffect(() => {
        if (!accessToken) return
        loadPage(true)
    }, [accessToken, loadPage])

    const loadMore = useCallback(() => {
        if (!isFetching.current && hasMoreRef.current) loadPage(false)
    }, [loadPage])

    return { items, loading, loadingMore, error, hasMore, loadMore }
}
