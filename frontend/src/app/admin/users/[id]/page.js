'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import ContentHistory from '@/components/content-history';

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

export default function UserProfilePage() {
  const { id } = useParams();
  const router = useRouter();
  
  const [user, setUser] = useState(null);
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    fetchUserContents(true);
  }, [id]);

  const fetchUserContents = async (reset = false) => {
    try {
      setLoading(true);
      setError(null);

      const currentPage = reset ? 1 : page;
      if (reset) {
        setPage(1);
        setContents([]);
      }

      const response = await api.getUserContents({
        userId: id,
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
      
      if (reset) {
        setContents(mappedItems);
      } else {
        setContents(prev => [...prev, ...mappedItems]);
      }
    } catch (error) {
      console.error('Error fetching user contents:', error);
      
      // Handle specific error cases
      if (error.message.includes('Authentication failed') || error.message.includes('401')) {
        toast({
          title: "Authentication Error",
          description: "Please log in to view this content",
          variant: "destructive"
        });
        router.push('/login');
        return;
      }
      
      if (error.message.includes('404') || error.message.includes('not found')) {
        toast({
          title: "User Not Found",
          description: "The requested user profile does not exist",
          variant: "destructive"
        });
        router.push('/');
        return;
      }
      
      setError('Failed to load user contents. Please try again later.');
      toast({
        title: "Error",
        description: "Failed to load user contents. Please try again later.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
      fetchUserContents(false);
    }
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button
            onClick={() => fetchUserContents(true)}
            variant="secondary"
            className="mr-2"
          >
            Retry
          </Button>
          <Button
            onClick={() => router.push('/')}
            variant="outline"
          >
            Go Home
          </Button>
        </div>
      </div>
    );
  }

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
    <div className="container px-4 py-8 mx-auto">
      <div className="mb-8">
        <Button
          variant="outline"
          onClick={() => router.back()}
          className="mb-4"
        >
          Back
        </Button>
        <h1 className="text-3xl font-bold">User Profile</h1>
        {user && (
          <p className="text-muted-foreground mt-1">
            {user.name} ({user.email})
          </p>
        )}
      </div>

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
          <ContentHistory contents={contents} admin={true} />
          
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
    </div>
  );
} 