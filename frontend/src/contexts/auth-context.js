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
        throw new Error(data.detail || 'Signup failed');
      }

      localStorage.setItem('token', data.access_token);
      toast.success('Account created successfully! Please check your email for verification.');
      router.push('/login');
      return data;
    } catch (error) {
      const errorMessage = error.message;
      if (errorMessage.includes('already registered')) {
        toast.error('This email is already registered. Please try logging in instead.');
      } else if (errorMessage.includes('validation failed')) {
        toast.error('Please check your email and password format.');
      } else if (errorMessage.includes('connect')) {
        toast.error('Unable to connect to the server. Please try again later.');
      } else {
        toast.error('Failed to create account. Please try again.');
      }
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
        const errorMessage = data.detail || 'Login failed';
        logger.error(`Login failed: ${errorMessage}`);
        throw new Error(errorMessage);
      }

      localStorage.setItem('token', data.access_token);
      await mutate();
      
      toast.success('Welcome back!');
      router.push('/');
      return data;
    } catch (error) {
      const errorMessage = error.message;
      if (errorMessage.includes('Invalid email or password')) {
        toast.error('Invalid email or password. Please try again.');
      } else if (errorMessage.includes('connect')) {
        toast.error('Unable to connect to the server. Please try again later.');
      } else {
        toast.error('Login failed. Please try again.');
      }
      throw error;
    }
  }, [router, mutate]);

  const logout = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const response = await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Logout failed');
        }
      }

      localStorage.removeItem('token');
      await mutate(null);
      router.replace('/login');
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      localStorage.removeItem('token');
      router.replace('/login');
      toast.error('There was an issue during logout, but you have been logged out successfully');
    }
  }, [router, mutate]);

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
        throw new Error(data.detail || 'Failed to send reset email');
      }

      toast.success('Password reset instructions have been sent to your email. Please check your inbox.');
      return data;
    } catch (error) {
      const errorMessage = error.message;
      if (errorMessage.includes('not found')) {
        toast.error('No account found with this email address.');
      } else if (errorMessage.includes('connect')) {
        toast.error('Unable to connect to the server. Please try again later.');
      } else if (errorMessage.includes('rate limit')) {
        toast.error('Too many reset attempts. Please try again later.');
      } else {
        toast.error('Failed to send reset email. Please try again.');
      }
      throw error;
    }
  }, []);

  const resetPassword = useCallback(async (token, newPassword) => {
    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          token,
          new_password: newPassword 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to reset password');
      }

      toast.success('Password has been reset successfully. Please login with your new password.');
      router.push('/login');
      return data;
    } catch (error) {
      const errorMessage = error.message;
      if (errorMessage.includes('Invalid') || errorMessage.includes('expired')) {
        toast.error('The password reset link has expired or is invalid. Please request a new one.');
        router.push('/forgot-password');
      } else if (errorMessage.includes('connect')) {
        toast.error('Unable to connect to the server. Please try again later.');
      } else {
        toast.error('Failed to reset password. Please try again.');
      }
      throw error;
    }
  }, [router]);

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