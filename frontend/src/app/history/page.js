'use client';

import { useState, useEffect } from 'react';
import ContentHistory from '@/components/content-history';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

const CONTENT_TYPES = [
  { label: 'All', value: null },
  { label: 'PDFs', value: 'PDF' },
  { label: 'Chat', value: 'CHAT' },
  { label: 'Voice', value: 'VOICE' },
  { label: 'Files', value: 'FILE' },
  { label: 'Bangla Chat', value: 'CHATBOT' },
  { label: 'Bangla Story', value: 'BENGALI_STORY' },
  { label: 'Bangla Translation', value: 'BENGALI_TRANSLATION' },
];

const ITEMS_PER_PAGE = 10;

export default function HistoryPage() {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    loadContents(true);
  }, [activeFilter]);

  const loadContents = async (reset = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const currentPage = reset ? 1 : page;
      if (reset) {
        setPage(1);
        setContents([]);
      }

      const response = await api.getContents({
        contentType: activeFilter,
        page: currentPage,
        limit: ITEMS_PER_PAGE,
        sortBy: 'createdAt',
        sortOrder: 'desc'
      });

      // Handle array response format
      const items = Array.isArray(response) ? response : [];
      
      // Map id to _id for consistency
      const mappedItems = items.map(item => ({
        ...item,
        _id: item.id
      }));

      // Estimate if there are more items based on the response length
      const hasMoreItems = items.length === ITEMS_PER_PAGE;
      
      setHasMore(hasMoreItems);
      setTotalItems(prev => reset ? items.length : prev + items.length);
      
      if (reset) {
        setContents(mappedItems);
      } else {
        setContents(prev => [...prev, ...mappedItems]);
      }
    } catch (error) {
      console.error('Error loading contents:', error);
      setError('Failed to load content history');
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
      loadContents(false);
    }
  };

  const handleDelete = (deletedId) => {
    setContents(contents.filter(content => content._id !== deletedId));
    setTotalItems(prev => prev - 1);
  };

  const handleFilterChange = (type) => {
    setActiveFilter(type);
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>{error}</p>
          <Button
            onClick={() => loadContents(true)}
            className="mt-4"
            variant="secondary"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Content History</h1>
          <p className="text-muted-foreground mt-1">
            {totalItems} {totalItems === 1 ? 'item' : 'items'} loaded
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {CONTENT_TYPES.map((type) => (
            <Button
              key={type.value || 'all'}
              variant={activeFilter === type.value ? "default" : "outline"}
              onClick={() => handleFilterChange(type.value)}
              className="min-w-[80px]"
            >
              {type.label}
            </Button>
          ))}
        </div>
      </div>

      {loading && contents.length === 0 ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : contents.length === 0 ? (
        <div className="text-center">
          <p className="text-muted-foreground">
            {activeFilter 
              ? `No ${activeFilter.toLowerCase()} content found`
              : 'No content history found'
            }
          </p>
        </div>
      ) : (
        <>
          <ContentHistory contents={contents} onDelete={handleDelete} />
          
          {hasMore && (
            <div className="mt-8 text-center">
              <Button
                variant="outline"
                onClick={loadMore}
                disabled={loading}
                className="min-w-[200px]"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
} 