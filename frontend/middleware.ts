import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Add routes that require authentication
const protectedRoutes = ['/dashboard', '/chat', '/admin'];
const authRoutes = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // If it's an API route, let the request continue
  if (path.startsWith("/api/")) {
    return NextResponse.next();
  }

  // Get the token from cookies
  const token = request.cookies.get("token")?.value;
  const isProtectedRoute = protectedRoutes.some(route => path.startsWith(route));
  const isAuthRoute = authRoutes.some(route => path === route);

  // Handle admin routes separately
  if (path.startsWith("/admin") && path !== "/admin/login") {
    const adminToken = request.cookies.get("adminToken")?.value;
    if (!adminToken) {
      const loginUrl = new URL("/admin/login", request.url);
      loginUrl.searchParams.set("from", path);
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  // If it's a protected route and no token exists, redirect to login
  if (isProtectedRoute && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", path);
    return NextResponse.redirect(loginUrl);
  }

  // If it's an auth route and token exists, redirect to dashboard
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public/*)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|_next/data).*)",
  ],
};
