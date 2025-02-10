'use client';

import Link from "next/link";
import { MessageSquare, LayoutDashboard, Building2 } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";
import { UserMenu } from "./UserMenu";
import { getUserToken } from "@/lib/auth";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = () => {
      const token = getUserToken();
      setIsLoggedIn(!!token);
      
      // If not logged in and on a protected route, redirect to auth
      if (!token && (pathname.startsWith('/chat') || pathname.startsWith('/dashboard'))) {
        router.push('/auth');
      }
    };

    // Check auth status initially
    checkAuth();

    // Set up an interval to check auth status
    const interval = setInterval(checkAuth, 1000 * 60); // Check every minute

    // Add event listener for storage changes (in case token is modified in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token' || e.key === 'logout-event') {
        checkAuth();
      }
    };
    window.addEventListener('storage', handleStorageChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [pathname, router]);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2 mr-6">
          <Building2 className="h-6 w-6 text-primary" />
          <span className="hidden font-bold sm:inline-block">
            CRE Assistant
          </span>
        </Link>

        {/* Centered Navigation - Only show when logged in */}
        {isLoggedIn && (
          <div className="flex-1 flex justify-center gap-6 md:gap-10">
            <Link href="/chat" className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span className="font-medium">Chat</span>
            </Link>
            <Link href="/dashboard" className="flex items-center space-x-2">
              <LayoutDashboard className="h-5 w-5" />
              <span className="font-medium">Dashboard</span>
            </Link>
          </div>
        )}
        
        {/* Spacer when not logged in */}
        {!isLoggedIn && <div className="flex-1" />}

        {/* Right Side - Theme Toggle & Auth */}
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          {isLoggedIn ? (
            <UserMenu />
          ) : (
            <div className="flex items-center space-x-2">
              <Link href="/auth?mode=login">
                <Button variant="ghost">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth?mode=register">
                <Button variant="default">
                  Sign Up
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}