import { NextResponse } from "next/server"

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { tool, operation, values } = body

    // Make API call to your Python backend
    const response = await fetch(`${process.env.BACKEND_URL}/calculate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tool,
        operation,
        values,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || "Calculation failed")
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Calculation error:", error)
    return NextResponse.json(
      { error: "Failed to perform calculation" },
      { status: 500 }
    )
  }
}
