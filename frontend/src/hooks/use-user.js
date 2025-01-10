import useSWR from 'swr';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const fetcher = async (url) => {
  const token = localStorage.getItem('token');
  
  // Don't make the request if there's no token
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      // Clear invalid token
      localStorage.removeItem('token');
      return null;
    }

    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }

    return response.json();
  } catch (error) {
    // Clear token on network errors or invalid JSON
    localStorage.removeItem('token');
    throw error;
  }
};

export function useUser() {
  const { data: user, error, isLoading, mutate } = useSWR(
    `${API_BASE_URL}/api/auth/me`,
    fetcher,
    {
      revalidateOnFocus: false,
      shouldRetryOnError: false,
      // Add some reasonable delays between retries
      onErrorRetry: (error, key, config, revalidate, { retryCount }) => {
        if (retryCount >= 3) return; // Give up after 3 retries
        if (error.status === 401) return; // Don't retry on auth errors

        // Exponential backoff
        setTimeout(() => revalidate({ retryCount }), 
          Math.min(1000 * (2 ** retryCount), 30000)
        );
      },
    }
  );

  return {
    user,
    isLoading,
    isError: error,
    mutate,
  };
}