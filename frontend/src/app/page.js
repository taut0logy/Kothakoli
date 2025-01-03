'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Toggle } from '@/components/ui/toggle'
import { Card } from '@/components/ui/card'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { useDebounce } from '@/hooks/use-debounce'
import { Loader2 } from 'lucide-react'
import Link from 'next/link'
import SearchUser from '@/components/search-user'

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [searchType, setSearchType] = useState('users')
  const [searchResults, setSearchResults] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const debouncedQuery = useDebounce(searchQuery, 300)

  useEffect(() => {
    if (debouncedQuery.trim()) {
      performSearch(debouncedQuery, 1)
    } else {
      setSearchResults([])
      setTotalPages(1)
      setPage(1)
      setHasMore(false)
    }
  }, [debouncedQuery, searchType])

  const performSearch = async (query, currentPage) => {
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const response = searchType === 'users'
        ? await api.searchUsers(query, currentPage)
        : await api.searchPdfs(query, currentPage)

      if (currentPage === 1) {
        setSearchResults(response.items || [])
      } else {
        setSearchResults(prev => [...prev, ...(response.items || [])])
      }
      
      setTotalPages(response.total_pages || 1)
      setHasMore(currentPage < (response.total_pages || 1))
    } catch (error) {
      toast.error('Failed to search. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const loadMore = () => {
    if (!isLoading && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      performSearch(debouncedQuery, nextPage)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      <div className="w-full mb-8">
        <SearchUser />
      </div>
    </div>
  )
} 