import { NextResponse } from "next/server";

export async function GET(request: Request) {
  try {
    const authHeader = request.headers.get("authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return new NextResponse(
        JSON.stringify({ error: "Missing or invalid token" }),
        { status: 401 }
      );
    }

    const token = authHeader.split(" ")[1];
    const response = await fetch(
      `${process.env.BACKEND_URL}/api/users/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      return new NextResponse(
        JSON.stringify({ error: "Failed to fetch user data" }),
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching user data:", error);
    return new NextResponse(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500 }
    );
  }
}
