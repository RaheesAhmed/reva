'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Building2 } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';
import { loginUser, registerUser, setAuthCookies } from '@/lib/auth';
import { useToast } from "@/hooks/use-toast";

interface AuthFormProps {
  mode: 'login' | 'register';
}

export function AuthForm({ mode }: AuthFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error when user types
  };

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Validation
      if (!formData.email || !formData.password) {
        throw new Error('Please fill in all required fields');
      }

      if (mode === 'register') {
        if (!formData.name) {
          throw new Error('Please enter your full name');
        }
        if (formData.password !== formData.confirmPassword) {
          throw new Error('Passwords do not match');
        }
        if (formData.password.length < 6) {
          throw new Error('Password must be at least 6 characters long');
        }
      }

      // Make API request
      const response = mode === 'login' 
        ? await loginUser(formData.email, formData.password)
        : await registerUser({
            email: formData.email,
            password: formData.password,
            name: formData.name
          });

      // Show success message
      toast({
        title: mode === 'login' ? "Welcome back!" : "Registration successful!",
        description: response.message,
        duration: mode === 'login' ? 3000 : 10000, // Show registration message longer
      });

      // Only set auth cookies and redirect if we have tokens (login case)
      if (response.access_token && response.refresh_token) {
        setAuthCookies(response);
        router.push('/dashboard');
        router.refresh();
      }
    } catch (error) {
      console.error('Auth error:', error);
      let errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      
      // Handle specific error messages
      if (errorMessage.includes('30 seconds')) {
        errorMessage = 'Please wait 30 seconds before trying again.';
      } else if (errorMessage.includes('already exists')) {
        errorMessage = 'An account with this email already exists. Please try logging in instead.';
      } else if (errorMessage.includes('Invalid login credentials')) {
        errorMessage = 'Invalid email or password. Please try again.';
      } else if (errorMessage.includes('Email not confirmed')) {
        errorMessage = 'Please check your email and click the confirmation link before logging in.';
      }
      
      setError(errorMessage);
      
      // Show error toast
      toast({
        variant: "destructive",
        title: "Error",
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
      <div className="flex flex-col space-y-2 text-center">
        <div className="flex items-center justify-center">
          <Building2 className="h-8 w-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">
          {mode === 'login' ? 'Welcome back' : 'Create an account'}
        </h1>
        <p className="text-sm text-gray-500">
          {mode === 'login' 
            ? 'Enter your email to sign in to your account' 
            : 'Enter your email below to create your account'}
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded-md text-sm">
          {error}
        </div>
      )}

      <div className="grid gap-6">
        <form onSubmit={onSubmit}>
          <div className="grid gap-4">
            {mode === 'register' && (
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  name="name"
                  placeholder="John Doe"
                  type="text"
                  value={formData.name}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  required
                />
              </div>
            )}
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                placeholder="name@example.com"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                autoCapitalize="none"
                autoComplete="email"
                autoCorrect="off"
                disabled={isLoading}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                autoCapitalize="none"
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                autoCorrect="off"
                disabled={isLoading}
                required
              />
            </div>
            {mode === 'register' && (
              <div className="grid gap-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  autoCapitalize="none"
                  autoComplete="new-password"
                  autoCorrect="off"
                  disabled={isLoading}
                  required
                />
              </div>
            )}
            <Button disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
              {isLoading && (
                <svg
                  className="mr-2 h-4 w-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              )}
              {mode === 'login' ? 'Sign In' : 'Sign Up'}
            </Button>
          </div>
        </form>
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-gray-500">
              Or continue with
            </span>
          </div>
        </div>
       
      </div>

      <p className="px-8 text-center text-sm text-gray-500">
        {mode === 'login' ? (
          <>
            Don't have an account?{' '}
            <Link href="/signup" className="underline hover:text-blue-600">
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <Link href="/login" className="underline hover:text-blue-600">
              Sign in
            </Link>
          </>
        )}
      </p>
    </div>
  );
}
