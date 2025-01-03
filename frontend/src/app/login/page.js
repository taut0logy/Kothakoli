'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from '@/contexts/auth-context';
import { FormError } from '@/components/ui/form-error';
import { useFormError } from '@/hooks/use-form-error';

export default function Login() {
  const router = useRouter();
  const { login, loading } = useAuth();
  const { serverError, handleError, setServerError } = useFormError();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    try {
      await login(formData);
      toast.success("Login successful");
      router.push('/dashboard');
    } catch (error) {
      handleError(error);
    }
  };

  return (
    <div className="container mx-auto p-4 pt-6">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">Login</CardTitle>
          </CardHeader>
          <CardContent>
            <FormError error={serverError} />
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Logging in...
                  </>
                ) : (
                  "Login"
                )}
              </Button>

              <div className="text-center text-sm">
                <span className="text-muted-foreground">Don't have an account? </span>
                <Button
                  variant="link"
                  className="p-0 h-auto font-semibold"
                  onClick={() => router.push('/signup')}
                >
                  Sign up
                </Button>
              </div>

              <div className="text-center">
                <Button
                  variant="link"
                  className="p-0 h-auto text-sm text-muted-foreground"
                  onClick={() => router.push('/forgot-password')}
                >
                  Forgot your password?
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 