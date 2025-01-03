'use client';

import { useState, useEffect } from 'react';
import ContentHistory from '@/components/content-history';
import { api } from '@/lib/api';

export default function HistoryPage() {
  const [contents, setContents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadContents();
  }, []);

  const loadContents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getContents();
      setContents(response);
    } catch (error) {
      console.error('Error loading contents:', error);
      setError('Failed to load content history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (deletedId) => {
    setContents(contents.filter(content => content.id !== deletedId));
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>{error}</p>
          <button
            onClick={loadContents}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8">
      {contents.length === 0 ? (
        <p className="text-center text-gray-500">No content history found</p>
      ) : (
        <ContentHistory contents={contents} onDelete={handleDelete} />
      )}
    </div>
  );
} 