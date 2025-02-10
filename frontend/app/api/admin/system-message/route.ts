import { NextResponse } from "next/server";

export async function GET(request: Request) {
  try {
    const response = await fetch(`${process.env.BACKEND_URL}/api/system-message`, {
      headers: {
        Authorization: request.headers.get("Authorization") || "",
      },
    });

    if (!response.ok) {
      return new NextResponse(
        JSON.stringify({ error: "Failed to fetch system message" }),
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching system message:", error);
    return new NextResponse(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch(`${process.env.BACKEND_URL}/api/system-message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: request.headers.get("Authorization") || "",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new NextResponse(
        JSON.stringify({ error: "Failed to update system message" }),
        { status: response.status }
      );
    }

    return NextResponse.json({ message: "System message updated successfully" });
  } catch (error) {
    console.error("Error updating system message:", error);
    return new NextResponse(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500 }
    );
  }
}
