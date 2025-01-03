'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { Icons } from '@/components/ui/icons';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/auth-context';
import { FormError } from '@/components/ui/form-error';
import { useFormError } from '@/hooks/use-form-error';
import { AlertCircle } from 'lucide-react';

const formSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { forgotPassword } = useAuth();
  const { serverError, handleError, setServerError } = useFormError();

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: '',
    },
  });

  const onSubmit = async (values) => {
    setLoading(true);
    setServerError('');
    try {
      await forgotPassword(values.email);
      setSuccess(true);
    } catch (error) {
      handleError(error, form);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container flex h-screen w-screen flex-col items-center justify-center">
        <Card className="w-[350px]">
          <CardHeader>
            <CardTitle>Check your email</CardTitle>
            <CardDescription>
              We've sent you a password reset link. Please check your email.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <Button asChild>
              <Link href="/login">Back to login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Forgot password</CardTitle>
          <CardDescription>
            Enter your email address and we'll send you a reset link
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FormError error={serverError} />
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="john@example.com" 
                          type="email" 
                          {...field} 
                          className={form.formState.errors.email ? "border-red-500 pr-10" : ""}
                        />
                        {form.formState.errors.email && (
                          <AlertCircle className="h-4 w-4 absolute right-3 top-3 text-red-500" />
                        )}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                    Sending reset link...
                  </>
                ) : (
                  'Send reset link'
                )}
              </Button>
            </form>
          </Form>
          <div className="mt-4 text-center text-sm">
            <Link
              href="/login"
              className="text-muted-foreground hover:text-primary"
            >
              Back to login
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 