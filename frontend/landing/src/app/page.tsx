"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Mic, Search, FileText, Zap, Shield, Users, ArrowRight, CheckCircle, Star } from "lucide-react";

export default function Home() {
    const [isLoginOpen, setIsLoginOpen] = useState(false);
    const [isSignupOpen, setIsSignupOpen] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token in localStorage
                localStorage.setItem("token", data.token);
                localStorage.setItem("user", JSON.stringify(data.user));
                setIsLoginOpen(false);
                alert("Login successful!");
            } else {
                alert(data.error || "Login failed");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Login failed. Please try again.");
        }
    };

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        const name = formData.get("name") as string;
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        try {
            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password, name })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token in localStorage
                localStorage.setItem("token", data.token);
                localStorage.setItem("user", JSON.stringify(data.user));
                setIsSignupOpen(false);
                alert("Registration successful!");
            } else {
                alert(data.error || "Registration failed");
            }
        } catch (error) {
            console.error("Signup error:", error);
            alert("Registration failed. Please try again.");
        }
    };

    const handleAppAccess = (appType: string) => {
        // Redirect to the appropriate application
        if (appType === "aisearch") {
            router.push("/aisearch");
        } else if (appType === "support") {
            router.push("/support");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
            {/* Navigation */}
            <nav className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-sm">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between py-4">
                        <div className="flex items-center space-x-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
                                <Search className="h-5 w-5 text-white" />
                            </div>
                            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-xl font-bold text-transparent">
                                AI Search VoiceRAG
                            </span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
                                <DialogTrigger asChild>
                                    <Button variant="ghost">Sign In</Button>
                                </DialogTrigger>
                                <DialogContent className="sm:max-w-[425px]">
                                    <DialogHeader>
                                        <DialogTitle>Welcome Back</DialogTitle>
                                        <DialogDescription>Sign in to access your AI-powered document search applications.</DialogDescription>
                                    </DialogHeader>
                                    <form onSubmit={handleLogin} className="space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="email">Email</Label>
                                            <Input id="email" name="email" type="email" placeholder="Enter your email" required />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="password">Password</Label>
                                            <Input id="password" name="password" type="password" placeholder="Enter your password" required />
                                        </div>
                                        <Button type="submit" className="w-full">
                                            Sign In
                                        </Button>
                                    </form>
                                </DialogContent>
                            </Dialog>

                            <Dialog open={isSignupOpen} onOpenChange={setIsSignupOpen}>
                                <DialogTrigger asChild>
                                    <Button>Get Started</Button>
                                </DialogTrigger>
                                <DialogContent className="sm:max-w-[425px]">
                                    <DialogHeader>
                                        <DialogTitle>Create Account</DialogTitle>
                                        <DialogDescription>Join thousands of users leveraging AI for intelligent document search.</DialogDescription>
                                    </DialogHeader>
                                    <form onSubmit={handleSignup} className="space-y-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="name">Full Name</Label>
                                            <Input id="name" name="name" type="text" placeholder="Enter your full name" required />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="signup-email">Email</Label>
                                            <Input id="signup-email" name="email" type="email" placeholder="Enter your email" required />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="signup-password">Password</Label>
                                            <Input id="signup-password" name="password" type="password" placeholder="Create a password" required />
                                        </div>
                                        <Button type="submit" className="w-full">
                                            Create Account
                                        </Button>
                                    </form>
                                </DialogContent>
                            </Dialog>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="px-4 py-20 sm:px-6 lg:px-8">
                <div className="mx-auto max-w-7xl">
                    <div className="text-center">
                        <Badge variant="secondary" className="mb-4">
                            <Star className="mr-1 h-4 w-4" />
                            Powered by Azure AI
                        </Badge>
                        <h1 className="mb-6 text-4xl font-bold text-gray-900 sm:text-6xl">
                            Intelligent Document Search
                            <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">with Voice AI</span>
                        </h1>
                        <p className="mx-auto mb-8 max-w-3xl text-xl text-gray-600">
                            Experience the future of document interaction. Ask questions naturally, get instant answers with source citations, and explore your
                            documents like never before.
                        </p>
                        <div className="flex flex-col justify-center gap-4 sm:flex-row">
                            <Button size="lg" className="px-8 py-6 text-lg" onClick={() => setIsSignupOpen(true)}>
                                Start Free Trial
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Button>
                            <Button size="lg" variant="outline" className="px-8 py-6 text-lg">
                                Watch Demo
                            </Button>
                        </div>
                    </div>

                    {/* Demo Preview */}
                    <div className="relative mt-16">
                        <div className="mx-auto max-w-4xl rounded-2xl bg-white p-8 shadow-2xl">
                            <div className="mb-6 flex items-center justify-center space-x-4">
                                <div className="flex h-12 w-12 cursor-pointer items-center justify-center rounded-full bg-red-500 transition-colors hover:bg-red-600">
                                    <Mic className="h-6 w-6 text-white" />
                                </div>
                                <div className="flex-1 rounded-full bg-gray-100 px-4 py-3">
                                    <p className="text-gray-500">Ask me anything about your documents...</p>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <div className="rounded-lg border-l-4 border-blue-500 bg-blue-50 p-4">
                                    <p className="text-gray-800">
                                        &ldquo;According to Bernoulli&apos;s principle, as the speed of a fluid increases, its pressure decreases...&rdquo;
                                    </p>
                                    <div className="mt-2 flex items-center text-sm text-gray-600">
                                        <FileText className="mr-1 h-4 w-4" />
                                        Source: physics_fluid_dynamics.pdf (Lines 45-52)
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="bg-white py-20">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold text-gray-900 sm:text-4xl">Powerful Features for Modern Document Search</h2>
                        <p className="mx-auto max-w-3xl text-xl text-gray-600">
                            Built with cutting-edge AI technology to revolutionize how you interact with documents.
                        </p>
                    </div>

                    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                                    <Mic className="h-6 w-6 text-blue-600" />
                                </div>
                                <CardTitle>Voice-Powered Search</CardTitle>
                                <CardDescription>
                                    Ask questions naturally using voice commands. Get instant, accurate responses with full context.
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
                                    <FileText className="h-6 w-6 text-green-600" />
                                </div>
                                <CardTitle>Source Citations</CardTitle>
                                <CardDescription>Every answer includes precise source references with page numbers and line locations.</CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
                                    <Zap className="h-6 w-6 text-purple-600" />
                                </div>
                                <CardTitle>Lightning Fast</CardTitle>
                                <CardDescription>
                                    Powered by Azure AI Search for sub-second response times, even with large document collections.
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
                                    <Shield className="h-6 w-6 text-orange-600" />
                                </div>
                                <CardTitle>Enterprise Security</CardTitle>
                                <CardDescription>Bank-level security with user isolation, encrypted communications, and compliance-ready.</CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-pink-100">
                                    <Users className="h-6 w-6 text-pink-600" />
                                </div>
                                <CardTitle>Multi-User Support</CardTitle>
                                <CardDescription>Support agent platform with conversation history, user management, and team collaboration.</CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100">
                                    <Search className="h-6 w-6 text-indigo-600" />
                                </div>
                                <CardTitle>Advanced Analytics</CardTitle>
                                <CardDescription>Deep insights into document usage, search patterns, and performance metrics.</CardDescription>
                            </CardHeader>
                        </Card>
                    </div>
                </div>
            </section>

            {/* Applications Section */}
            <section className="bg-gray-50 py-20">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold text-gray-900 sm:text-4xl">Choose Your Experience</h2>
                        <p className="mx-auto max-w-3xl text-xl text-gray-600">
                            Two powerful applications designed for different use cases and user experiences.
                        </p>
                    </div>

                    <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-2">
                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <CardTitle className="text-2xl">AI Search VoiceRAG</CardTitle>
                                <CardDescription className="text-lg">
                                    Streamlined voice-powered document search for individual users and small teams.
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ul className="mb-6 space-y-3">
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Voice-activated search
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Real-time responses
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Source citations
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        PDF document support
                                    </li>
                                </ul>
                                <Button className="w-full" onClick={() => handleAppAccess("aisearch")}>
                                    Launch AI Search
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                            <CardHeader>
                                <CardTitle className="text-2xl">Support Agent Platform</CardTitle>
                                <CardDescription className="text-lg">
                                    Comprehensive support platform with advanced features for teams and enterprises.
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ul className="mb-6 space-y-3">
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Multi-user support
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Conversation history
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Document management
                                    </li>
                                    <li className="flex items-center">
                                        <CheckCircle className="mr-3 h-5 w-5 text-green-500" />
                                        Advanced analytics
                                    </li>
                                </ul>
                                <Button className="w-full" onClick={() => handleAppAccess("support")}>
                                    Launch Support Agent
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 py-12 text-white">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="grid gap-8 md:grid-cols-4">
                        <div>
                            <div className="mb-4 flex items-center space-x-2">
                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
                                    <Search className="h-5 w-5 text-white" />
                                </div>
                                <span className="text-xl font-bold">AI Search VoiceRAG</span>
                            </div>
                            <p className="text-gray-400">Revolutionizing document search with AI-powered voice interactions.</p>
                        </div>
                        <div>
                            <h3 className="mb-4 font-semibold">Product</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Features
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Pricing
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        API
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Documentation
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="mb-4 font-semibold">Company</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        About
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Blog
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Careers
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Contact
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="mb-4 font-semibold">Support</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Help Center
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Community
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Status
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="transition-colors hover:text-white">
                                        Privacy
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div className="mt-8 border-t border-gray-800 pt-8 text-center text-gray-400">
                        <p>&copy; 2025 AI Search VoiceRAG. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
