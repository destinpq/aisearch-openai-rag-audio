import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const { email, password, name } = await request.json();

        if (!email || !password || !name) {
            return NextResponse.json({ error: "Email, password, and name are required" }, { status: 400 });
        }

        // For demo purposes, we'll create a mock user
        // In a real application, you'd send this to your backend API
        const mockUser = {
            id: Date.now().toString(),
            email,
            name,
            subscription_tier: "free",
            credits_remaining: 100
        };

        // Create a simple JWT-like token (in production, use proper JWT)
        const token = Buffer.from(
            JSON.stringify({
                user_id: mockUser.id,
                email: mockUser.email,
                exp: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
            })
        ).toString("base64");

        return NextResponse.json(
            {
                token,
                user: mockUser,
                message: "Registration successful"
            },
            { status: 201 }
        );
    } catch (error) {
        console.error("Registration error:", error);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}
