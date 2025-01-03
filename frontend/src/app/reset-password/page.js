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
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from '@/components/ui/input-otp';
import { useAuth } from '@/contexts/auth-context';
import { FormError } from '@/components/ui/form-error';
import { useFormError } from '@/hooks/use-form-error';
import { AlertCircle } from 'lucide-react';

const formSchema = z.object({
  otp: z.string().length(6, 'Please enter a valid OTP'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export default function ResetPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { resetPassword } = useAuth();
  const { serverError, handleError, setServerError } = useFormError();

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      otp: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (values) => {
    setLoading(true);
    setServerError('');
    try {
      await resetPassword(values.otp, values.password);
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
            <CardTitle>Password reset successful</CardTitle>
            <CardDescription>
              Your password has been reset. You can now log in with your new password.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <Button asChild>
              <Link href="/login">Go to login</Link>
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
          <CardTitle>Reset password</CardTitle>
          <CardDescription>
            Enter the verification code and your new password
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FormError error={serverError} />
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="otp"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Verification Code</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <InputOTP
                          maxLength={6}
                          render={({ slots }) => (
                            <InputOTPGroup>
                              {slots.map((slot, index) => (
                                <InputOTPSlot key={index} {...slot} />
                              ))}
                            </InputOTPGroup>
                          )}
                          {...field}
                          className={form.formState.errors.otp ? "border-red-500" : ""}
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>New Password</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="••••••••" 
                          type="password" 
                          {...field} 
                          className={form.formState.errors.password ? "border-red-500 pr-10" : ""}
                        />
                        {form.formState.errors.password && (
                          <AlertCircle className="h-4 w-4 absolute right-3 top-3 text-red-500" />
                        )}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="confirmPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirm Password</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="••••••••" 
                          type="password" 
                          {...field} 
                          className={form.formState.errors.confirmPassword ? "border-red-500 pr-10" : ""}
                        />
                        {form.formState.errors.confirmPassword && (
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
                    Resetting password...
                  </>
                ) : (
                  'Reset password'
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