import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { Mic, Search, FileText, Zap, Shield, Globe, ArrowRight, CheckCircle } from "lucide-react";

function Landing() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    // Features data
    const features = [
        {
            icon: <Mic className="h-8 w-8 text-blue-600" />,
            title: "Voice-Powered AI",
            description: "Natural voice conversations with advanced AI that understands context and intent."
        },
        {
            icon: <Search className="h-8 w-8 text-green-600" />,
            title: "Intelligent Search",
            description: "Find exactly what you need with AI-powered search across your documents and the web."
        },
        {
            icon: <FileText className="h-8 w-8 text-purple-600" />,
            title: "PDF Processing",
            description: "Upload and analyze PDF documents with advanced text extraction and understanding."
        },
        {
            icon: <Shield className="h-8 w-8 text-red-600" />,
            title: "Secure & Private",
            description: "Your documents and conversations are protected with enterprise-grade security."
        },
        {
            icon: <Zap className="h-8 w-8 text-yellow-600" />,
            title: "Lightning Fast",
            description: "Get instant responses with our optimized AI infrastructure powered by Azure."
        },
        {
            icon: <Globe className="h-8 w-8 text-indigo-600" />,
            title: "Web Integration",
            description: "Search the entire web or focus on your personal document library."
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
            {/* Navigation */}
            <nav className="fixed top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between py-4">
                        <div className="flex items-center space-x-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
                                <Mic className="h-4 w-4 text-white" />
                            </div>
                            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-xl font-bold text-transparent">VoiceRAG</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <Link to="/login">
                                <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                                    Login
                                </Button>
                            </Link>
                            <Link to="/register">
                                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">Get Started</Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="px-4 pb-16 pt-24 sm:px-6 lg:px-8">
                <div className="mx-auto max-w-7xl">
                    <div className={`text-center transition-all duration-1000 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"}`}>
                        <h1 className="mb-6 text-4xl font-bold text-gray-900 sm:text-6xl lg:text-7xl">
                            The Future of
                            <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                                AI Conversations
                            </span>
                        </h1>
                        <p className="mx-auto mb-8 max-w-3xl text-xl leading-relaxed text-gray-600">
                            Experience natural voice interactions with AI that understands your documents, searches the web, and provides intelligent responses
                            powered by Azure AI and OpenAI.
                        </p>
                        <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row">
                            <Link to="/register">
                                <Button
                                    size="lg"
                                    className="rounded-full bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all duration-300 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl"
                                >
                                    Start Free Trial
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                            <Link to="/login">
                                <Button
                                    size="lg"
                                    variant="outline"
                                    className="rounded-full border-2 border-gray-300 px-8 py-4 text-lg font-semibold transition-all duration-300 hover:border-blue-500 hover:bg-blue-50"
                                >
                                    Login to Account
                                </Button>
                            </Link>
                        </div>
                    </div>

                    {/* Hero Visual */}
                    <div
                        className={`relative mx-auto mt-16 max-w-4xl transition-all delay-300 duration-1000 ${isVisible ? "scale-100 opacity-100" : "scale-95 opacity-0"}`}
                    >
                        <div className="rounded-2xl border border-white/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 p-8 backdrop-blur-sm">
                            <div className="rounded-xl bg-white p-6 shadow-2xl">
                                <div className="mb-4 flex items-center space-x-4">
                                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600">
                                        <Mic className="h-6 w-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="mb-2 h-3 rounded-full bg-gray-200"></div>
                                        <div className="h-3 w-3/4 rounded-full bg-gray-200"></div>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <div className="flex items-center space-x-3">
                                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500">
                                            <CheckCircle className="h-4 w-4 text-white" />
                                        </div>
                                        <div className="h-3 flex-1 rounded-full bg-gray-200"></div>
                                    </div>
                                    <div className="flex items-center space-x-3">
                                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500">
                                            <FileText className="h-4 w-4 text-white" />
                                        </div>
                                        <div className="h-3 flex-1 rounded-full bg-gray-200"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="bg-white px-4 py-16 sm:px-6 lg:px-8">
                <div className="mx-auto max-w-7xl">
                    <div className="mb-16 text-center">
                        <h2 className="mb-4 text-3xl font-bold text-gray-900 sm:text-4xl">Powerful Features for Modern AI Interaction</h2>
                        <p className="mx-auto max-w-2xl text-xl text-gray-600">
                            Everything you need to have intelligent conversations with your documents and data.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
                        {features.map((feature, index) => (
                            <div
                                key={index}
                                className="rounded-xl border border-gray-100 bg-gradient-to-br from-white to-gray-50 p-6 shadow-lg transition-all duration-300 hover:shadow-xl"
                            >
                                <div className="mb-4">{feature.icon}</div>
                                <h3 className="mb-2 text-xl font-semibold text-gray-900">{feature.title}</h3>
                                <p className="text-gray-600">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-16 sm:px-6 lg:px-8">
                <div className="mx-auto max-w-4xl text-center">
                    <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl">Ready to Transform Your Document Workflow?</h2>
                    <p className="mb-8 text-xl text-blue-100">Join thousands of professionals who are already using VoiceRAG to enhance their productivity.</p>
                    <div className="flex flex-col justify-center gap-4 sm:flex-row">
                        <Link to="/register">
                            <Button size="lg" className="rounded-full bg-white px-8 py-4 text-lg font-semibold text-blue-600 shadow-lg hover:bg-gray-100">
                                Start Your Free Trial
                            </Button>
                        </Link>
                        <Link to="/login">
                            <Button
                                size="lg"
                                variant="outline"
                                className="rounded-full border-white px-8 py-4 text-lg font-semibold text-white hover:bg-white hover:text-blue-600"
                            >
                                Login to Continue
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 px-4 py-12 text-white sm:px-6 lg:px-8">
                <div className="mx-auto max-w-7xl">
                    <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
                        <div className="col-span-1 md:col-span-2">
                            <div className="mb-4 flex items-center space-x-2">
                                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
                                    <Mic className="h-4 w-4 text-white" />
                                </div>
                                <span className="text-xl font-bold">VoiceRAG</span>
                            </div>
                            <p className="mb-4 text-gray-400">The future of AI-powered document interaction and voice conversations.</p>
                            <p className="text-sm text-gray-500">Powered by Azure AI Search and OpenAI</p>
                        </div>
                        <div>
                            <h3 className="mb-4 text-lg font-semibold">Product</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <Link to="/features" className="hover:text-white">
                                        Features
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/pricing" className="hover:text-white">
                                        Pricing
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/docs" className="hover:text-white">
                                        Documentation
                                    </Link>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="mb-4 text-lg font-semibold">Support</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <Link to="/help" className="hover:text-white">
                                        Help Center
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/contact" className="hover:text-white">
                                        Contact Us
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/login" className="hover:text-white">
                                        Login
                                    </Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div className="mt-8 border-t border-gray-800 pt-8 text-center text-gray-400">
                        <p>&copy; 2025 VoiceRAG. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default Landing;
