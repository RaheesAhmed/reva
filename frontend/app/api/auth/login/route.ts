import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { email, password } = body;

    console.log('Attempting login with email:', email);

    const response = await fetch(`${process.env.BACKEND_URL}/api/users/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    console.log('Login response status:', response.status);
    const data = await response.json();
    console.log('Login response data:', data);

    if (!response.ok) {
      console.error('Login failed:', data.detail);
      return NextResponse.json(
        { detail: data.detail || "Invalid credentials" },
        { status: response.status }
      );
    }

    // Set the cookie with the access token
    const cookieOptions = process.env.NODE_ENV === 'production'
      ? 'Path=/; Secure; HttpOnly; SameSite=Strict'
      : 'Path=/; SameSite=Strict';
    
    const headers = new Headers();
    headers.append('Set-Cookie', `userToken=${data.access_token}; ${cookieOptions}`);

    return NextResponse.json(data, {
      headers,
      status: 200,
    });
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
