import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { email, password, name, company } = body;

    console.log('Attempting registration with:', { email, name, company });

    const response = await fetch(`${process.env.BACKEND_URL}/api/users/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password, name, company }),
    });

    console.log('Backend response status:', response.status);
    const data = await response.json();
    console.log('Backend response data:', data);

    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || "Registration failed" },
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
    console.error("Registration error:", error);
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}
