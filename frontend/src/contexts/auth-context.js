'use client';

import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useUser } from '@/hooks/use-user';

const AuthContext = createContext({});

const publicPaths = ['/login', '/signup', '/verify-email', '/forgot-password', '/reset-password'];

export function AuthProvider({ children }) {
  const { user, isLoading, mutate } = useUser();
  const router = useRouter();

  const signup = useCallback(async (userData) => {
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          name: userData.name
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      localStorage.setItem('token', data.access_token);
      toast.success('Signup successful! Please verify your email.');
      router.push('/verify-email');
      return data;
    } catch (error) {
      toast.error('Signup failed. Please check the form for errors.');
      throw error;
    }
  }, [router]);

  const login = useCallback(async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      localStorage.setItem('token', data.access_token);
      await mutate();
      
      toast.success('Login successful!');
      router.push('/');
      return data;
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
      throw error;
    }
  }, [router, mutate]);

  const logout = useCallback(async () => {
    try {
      // Call backend logout endpoint
      const token = localStorage.getItem('token');
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }

      mutate();
      localStorage.removeItem('token');

      router.replace('/login');
      mutate();
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      localStorage.removeItem('token');
      document.cookie = `token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
      router.replace('/login');
      toast.error('Logged out with some errors');
    }
  }, [router]);

  const updateProfile = useCallback(async (userData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update profile');
      }

      toast.success('Profile updated successfully');
      return data;
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  }, []);

  const deleteAccount = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/me', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete account');
      }

      a
      localStorage.removeItem('token');
      router.push('/login');
      toast.success('Account deleted successfully');
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  }, [router]);

  const forgotPassword = useCallback(async (email) => {
    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      toast.success('Reset email sent successfully');
      return data;
    } catch (error) {
      toast.error('Failed to send reset email. Please try again.');
      throw error;
    }
  }, []);

  const resetPassword = useCallback(async (otp, password) => {
    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ otp, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      toast.success('Password reset successfully');
      return data;
    } catch (error) {
      toast.error('Failed to reset password. Please try again.');
      throw error;
    }
  }, []);

  // Use useEffect for initial auth check
  useEffect(() => {
    // Don't perform redirects while still loading
    if (isLoading) return;

    const currentPath = window.location.pathname;
    const isPublicPath = publicPaths.some(path => currentPath.startsWith(path));

    if (!user && !isPublicPath) {
      router.push('/login');
    } else if (user && isPublicPath) {
      router.push('/');
    }
  }, [user, isLoading, router]);

  const value = {
    login,
    signup,
    logout,
    updateProfile,
    deleteAccount,
    forgotPassword,
    resetPassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 