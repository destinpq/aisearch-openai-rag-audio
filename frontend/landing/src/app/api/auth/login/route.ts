import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
    try {
        const { email, password } = await request.json();

        if (!email || !password) {
            return NextResponse.json({ error: "Email and password are required" }, { status: 400 });
        }

        // For demo purposes, we'll accept any email/password combination
        // In a real application, you'd validate against your backend API
        const mockUser = {
            id: "1",
            email,
            name: email.split("@")[0],
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

        return NextResponse.json({
            token,
            user: mockUser,
            message: "Login successful"
        });
    } catch (error) {
        console.error("Login error:", error);
        return NextResponse.json({ error: "Internal server error" }, { status: 500 });
    }
}
