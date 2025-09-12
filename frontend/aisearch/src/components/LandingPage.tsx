import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Phone, MessageSquare, FileText, Zap, CheckCircle, Star, ArrowRight, Play, Mic, Search, Database, Smartphone } from "lucide-react";

interface LandingPageProps {
    onNavigateToApp: () => void;
}

export function LandingPage({ onNavigateToApp }: LandingPageProps) {
    const [email, setEmail] = useState("");

    const features = [
        {
            icon: <Mic className="h-8 w-8 text-blue-500" />,
            title: "Voice-Powered Search",
            description: "Ask questions naturally using your voice. No typing required."
        },
        {
            icon: <Search className="h-8 w-8 text-green-500" />,
            title: "Intelligent RAG",
            description: "Advanced retrieval-augmented generation for accurate, contextual answers."
        },
        {
            icon: <FileText className="h-8 w-8 text-purple-500" />,
            title: "Document Processing",
            description: "Upload PDFs and get instant answers with source citations."
        },
        {
            icon: <Phone className="h-8 w-8 text-red-500" />,
            title: "Phone Integration",
            description: "Call in anytime to get answers from your documents via phone."
        },
        {
            icon: <Database className="h-8 w-8 text-orange-500" />,
            title: "Conversation History",
            description: "Keep track of all your conversations and search through them."
        },
        {
            icon: <Smartphone className="h-8 w-8 text-indigo-500" />,
            title: "Multi-Device Access",
            description: "Access your documents and conversations from any device."
        }
    ];

    const testimonials = [
        {
            name: "Sarah Johnson",
            role: "Legal Assistant",
            content: "VoiceRAG has transformed how I work with legal documents. I can now get instant answers without flipping through hundreds of pages.",
            rating: 5
        },
        {
            name: "Dr. Michael Chen",
            role: "Research Scientist",
            content: "The phone integration is a game-changer. I can call in while driving and get answers to complex research questions instantly.",
            rating: 5
        },
        {
            name: "Emma Rodriguez",
            role: "Business Analyst",
            content: "Being able to search through multiple PDFs simultaneously and get accurate citations has saved me hours of work.",
            rating: 5
        }
    ];

    const pricingPlans = [
        {
            name: "Free",
            price: "$0",
            period: "forever",
            features: ["5 PDF uploads per month", "100 voice queries per month", "Basic conversation history", "Web interface only"],
            popular: false
        },
        {
            name: "Pro",
            price: "$19",
            period: "per month",
            features: ["Unlimited PDF uploads", "Unlimited voice queries", "Advanced conversation history", "Phone integration", "Priority support"],
            popular: true
        },
        {
            name: "Enterprise",
            price: "Custom",
            period: "pricing",
            features: ["Everything in Pro", "Custom integrations", "Advanced analytics", "Dedicated support", "SLA guarantees"],
            popular: false
        }
    ];

    const handleEmailSignup = (e: React.FormEvent) => {
        e.preventDefault();
        // Handle email signup
        console.log("Email signup:", email);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Header */}
            <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-sm">
                <div className="container mx-auto flex items-center justify-between px-4 py-4">
                    <div className="flex items-center space-x-2">
                        <div className="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 p-2">
                            <Mic className="h-6 w-6 text-white" />
                        </div>
                        <h1 className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-2xl font-bold text-transparent">VoiceRAG</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <Button variant="ghost" onClick={onNavigateToApp}>
                            Sign In
                        </Button>
                        <Button onClick={onNavigateToApp}>
                            Get Started
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="px-4 py-20">
                <div className="container mx-auto text-center">
                    <Badge className="mb-4 bg-blue-100 text-blue-700 hover:bg-blue-100">🚀 Now with Phone Integration</Badge>
                    <h1 className="mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-5xl font-bold text-transparent">
                        Talk to Your Documents
                    </h1>
                    <p className="mx-auto mb-8 max-w-3xl text-xl text-gray-600">
                        Transform your PDFs into an intelligent voice assistant. Ask questions naturally, get instant answers with source citations, and access
                        everything via phone or web.
                    </p>
                    <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
                        <Button
                            size="lg"
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                            onClick={onNavigateToApp}
                        >
                            <Play className="mr-2 h-5 w-5" />
                            Try VoiceRAG Free
                        </Button>
                        <Button size="lg" variant="outline" onClick={onNavigateToApp}>
                            <Phone className="mr-2 h-5 w-5" />
                            Call to Demo
                        </Button>
                    </div>
                    <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
                        <div className="flex items-center">
                            <CheckCircle className="mr-1 h-4 w-4 text-green-500" />
                            No setup required
                        </div>
                        <div className="flex items-center">
                            <CheckCircle className="mr-1 h-4 w-4 text-green-500" />
                            Works with any PDF
                        </div>
                        <div className="flex items-center">
                            <CheckCircle className="mr-1 h-4 w-4 text-green-500" />
                            Phone & web access
                        </div>
                    </div>
                </div>
            </section>

            {/* Demo Video Section */}
            <section className="bg-white px-4 py-16">
                <div className="container mx-auto">
                    <div className="mx-auto max-w-4xl text-center">
                        <h2 className="mb-4 text-3xl font-bold">See VoiceRAG in Action</h2>
                        <p className="mb-8 text-gray-600">Watch how easy it is to get answers from your documents</p>
                        <div className="flex h-96 items-center justify-center rounded-lg bg-gray-200">
                            <iframe
                                src="https://www.loom.com/embed/d0d6f1c4906042fdb8959ef8285a7fc4?sid=cf26fd78-23dd-4adc-9a17-6b1330b1bd6f"
                                allowFullScreen
                                frameBorder="0"
                                className="h-full w-full rounded-lg"
                                title="Demo Video"
                            ></iframe>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="px-4 py-20">
                <div className="container mx-auto">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold">Everything You Need</h2>
                        <p className="mx-auto max-w-2xl text-gray-600">
                            VoiceRAG combines the power of AI, voice technology, and document intelligence to revolutionize how you interact with your
                            information.
                        </p>
                    </div>
                    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                        {features.map((feature, index) => (
                            <Card key={index} className="border-0 shadow-lg transition-shadow hover:shadow-xl">
                                <CardHeader>
                                    <div className="mb-4">{feature.icon}</div>
                                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <CardDescription className="text-base">{feature.description}</CardDescription>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="bg-gray-50 px-4 py-20">
                <div className="container mx-auto">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold">How It Works</h2>
                        <p className="text-gray-600">Get started in just three simple steps</p>
                    </div>
                    <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-3">
                        <div className="text-center">
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
                                <FileText className="h-8 w-8 text-blue-600" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">1. Upload Documents</h3>
                            <p className="text-gray-600">Upload your PDFs through our web interface or call in to add documents via phone.</p>
                        </div>
                        <div className="text-center">
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-purple-100">
                                <MessageSquare className="h-8 w-8 text-purple-600" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">2. Ask Questions</h3>
                            <p className="text-gray-600">Speak naturally or type your questions. Our AI understands context and intent.</p>
                        </div>
                        <div className="text-center">
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                                <Zap className="h-8 w-8 text-green-600" />
                            </div>
                            <h3 className="mb-2 text-xl font-semibold">3. Get Answers</h3>
                            <p className="text-gray-600">Receive accurate answers with source citations and exact page/line references.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="px-4 py-20">
                <div className="container mx-auto">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold">Loved by Professionals</h2>
                        <p className="text-gray-600">See what our users say about VoiceRAG</p>
                    </div>
                    <div className="mx-auto grid max-w-6xl gap-8 md:grid-cols-3">
                        {testimonials.map((testimonial, index) => (
                            <Card key={index} className="border-0 shadow-lg">
                                <CardContent className="pt-6">
                                    <div className="mb-4 flex">
                                        {[...Array(testimonial.rating)].map((_, i) => (
                                            <Star key={i} className="h-5 w-5 fill-current text-yellow-400" />
                                        ))}
                                    </div>
                                    <p className="mb-4 text-gray-600">"{testimonial.content}"</p>
                                    <div>
                                        <p className="font-semibold">{testimonial.name}</p>
                                        <p className="text-sm text-gray-500">{testimonial.role}</p>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </section>

            {/* Pricing */}
            <section className="bg-gray-50 px-4 py-20">
                <div className="container mx-auto">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold">Simple, Transparent Pricing</h2>
                        <p className="text-gray-600">Choose the plan that's right for you</p>
                    </div>
                    <div className="mx-auto grid max-w-5xl gap-8 md:grid-cols-3">
                        {pricingPlans.map((plan, index) => (
                            <Card key={index} className={`relative ${plan.popular ? "border-blue-500 shadow-xl" : "border-0 shadow-lg"}`}>
                                {plan.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 transform">
                                        <Badge className="bg-blue-500 text-white">Most Popular</Badge>
                                    </div>
                                )}
                                <CardHeader className="text-center">
                                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                                    <div className="mt-4">
                                        <span className="text-4xl font-bold">{plan.price}</span>
                                        <span className="text-gray-500">/{plan.period}</span>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <ul className="space-y-3">
                                        {plan.features.map((feature, i) => (
                                            <li key={i} className="flex items-center">
                                                <CheckCircle className="mr-2 h-5 w-5 flex-shrink-0 text-green-500" />
                                                <span className="text-sm">{feature}</span>
                                            </li>
                                        ))}
                                    </ul>
                                    <Button
                                        className={`mt-6 w-full ${plan.popular ? "bg-blue-600 hover:bg-blue-700" : ""}`}
                                        variant={plan.popular ? "default" : "outline"}
                                        onClick={onNavigateToApp}
                                    >
                                        Get Started
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-20 text-white">
                <div className="container mx-auto text-center">
                    <h2 className="mb-4 text-3xl font-bold">Ready to Transform Your Document Workflow?</h2>
                    <p className="mx-auto mb-8 max-w-2xl text-xl opacity-90">
                        Join thousands of professionals who are already using VoiceRAG to work smarter, not harder.
                    </p>
                    <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
                        <Button size="lg" variant="secondary" onClick={onNavigateToApp}>
                            Start Free Trial
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                        <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                            Schedule Demo
                        </Button>
                    </div>
                    <p className="mt-4 text-sm opacity-75">No credit card required • 14-day free trial</p>
                </div>
            </section>

            {/* Newsletter Signup */}
            <section className="px-4 py-16">
                <div className="container mx-auto max-w-md">
                    <Card>
                        <CardHeader className="text-center">
                            <CardTitle>Stay Updated</CardTitle>
                            <CardDescription>Get the latest features and updates delivered to your inbox</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleEmailSignup} className="space-y-4">
                                <Input type="email" placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)} required />
                                <Button type="submit" className="w-full">
                                    Subscribe
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t bg-white px-4 py-12">
                <div className="container mx-auto">
                    <div className="grid gap-8 md:grid-cols-4">
                        <div>
                            <div className="mb-4 flex items-center space-x-2">
                                <div className="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 p-2">
                                    <Mic className="h-6 w-6 text-white" />
                                </div>
                                <h3 className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-xl font-bold text-transparent">VoiceRAG</h3>
                            </div>
                            <p className="text-gray-600">Revolutionizing document interaction with voice-powered AI.</p>
                        </div>
                        <div>
                            <h4 className="mb-4 font-semibold">Product</h4>
                            <ul className="space-y-2 text-gray-600">
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Features
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Pricing
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Security
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Integrations
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="mb-4 font-semibold">Company</h4>
                            <ul className="space-y-2 text-gray-600">
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        About
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Blog
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Careers
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Contact
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="mb-4 font-semibold">Support</h4>
                            <ul className="space-y-2 text-gray-600">
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Help Center
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        API Docs
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Status
                                    </a>
                                </li>
                                <li>
                                    <a href="#" className="hover:text-blue-600">
                                        Community
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <Separator className="my-8" />
                    <div className="flex flex-col items-center justify-between md:flex-row">
                        <p className="text-gray-600">© 2024 VoiceRAG. All rights reserved.</p>
                        <div className="mt-4 flex space-x-4 md:mt-0">
                            <a href="#" className="text-gray-600 hover:text-blue-600">
                                Privacy
                            </a>
                            <a href="#" className="text-gray-600 hover:text-blue-600">
                                Terms
                            </a>
                            <a href="#" className="text-gray-600 hover:text-blue-600">
                                Cookies
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
