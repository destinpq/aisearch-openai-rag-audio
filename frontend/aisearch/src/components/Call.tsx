import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Phone, PhoneCall, PhoneOff, Mic, Search, UploadIcon, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

import logo from "../assets/logo.svg";

function Call() {
    const [phoneNumber, setPhoneNumber] = useState("");
    const [isConnected, setIsConnected] = useState(false);
    const [callStatus, setCallStatus] = useState("idle");
    const { logout } = useAuth();

    const handleCall = () => {
        if (!phoneNumber) return;

        setIsConnected(true);
        setCallStatus("connecting");

        // Simulate call connection
        setTimeout(() => {
            setCallStatus("connected");
        }, 2000);
    };

    const handleEndCall = () => {
        setIsConnected(false);
        setCallStatus("idle");
        setPhoneNumber("");
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Navigation Header */}
            <header className="flex items-center justify-between bg-white p-4 shadow-md">
                <div className="flex items-center space-x-4">
                    <img src={logo} alt="Azure logo" className="h-8 w-8" />
                    <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text font-bold text-transparent">VoiceRAG</span>
                </div>
                <nav className="flex space-x-2">
                    <Link to="/app">
                        <Button variant="outline" size="sm">
                            <Mic className="mr-2 h-4 w-4" />
                            Voice Chat
                        </Button>
                    </Link>
                    <Link to="/upload">
                        <Button variant="outline" size="sm">
                            <UploadIcon className="mr-2 h-4 w-4" />
                            Upload
                        </Button>
                    </Link>
                    <Link to="/analyze">
                        <Button variant="outline" size="sm">
                            <Search className="mr-2 h-4 w-4" />
                            Analyze
                        </Button>
                    </Link>
                    <Link to="/call">
                        <Button size="sm" className="bg-blue-600">
                            <Phone className="mr-2 h-4 w-4" />
                            Call
                        </Button>
                    </Link>
                    <Button variant="outline" size="sm" onClick={logout}>
                        <LogOut className="mr-2 h-4 w-4" />
                        Logout
                    </Button>
                </nav>
            </header>

            {/* Main Content */}
            <div className="p-4">
                <div className="mx-auto max-w-2xl">
                    <Card className="bg-white shadow-lg">
                        <CardHeader className="text-center">
                            <CardTitle className="flex items-center justify-center text-3xl font-bold text-gray-900">
                                <Phone className="mr-3 h-8 w-8 text-blue-600" />
                                Voice Call
                            </CardTitle>
                            <p className="mt-2 text-gray-600">Make a voice call to interact with your documents</p>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {!isConnected ? (
                                <>
                                    <div>
                                        <label htmlFor="phone" className="mb-2 block text-sm font-medium text-gray-700">
                                            Phone Number
                                        </label>
                                        <input
                                            id="phone"
                                            type="tel"
                                            value={phoneNumber}
                                            onChange={e => setPhoneNumber(e.target.value)}
                                            placeholder="+1 (555) 123-4567"
                                            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <Button
                                        onClick={handleCall}
                                        disabled={!phoneNumber || callStatus === "connecting"}
                                        className="w-full bg-green-600 hover:bg-green-700"
                                        size="lg"
                                    >
                                        {callStatus === "connecting" ? (
                                            <>
                                                <PhoneCall className="mr-2 h-5 w-5 animate-pulse" />
                                                Connecting...
                                            </>
                                        ) : (
                                            <>
                                                <PhoneCall className="mr-2 h-5 w-5" />
                                                Start Call
                                            </>
                                        )}
                                    </Button>
                                </>
                            ) : (
                                <div className="space-y-6 text-center">
                                    <div className="space-y-2">
                                        <div className="inline-flex items-center rounded-full bg-green-100 px-4 py-2 text-green-800">
                                            <PhoneCall className="mr-2 h-4 w-4" />
                                            {callStatus === "connecting" ? "Connecting..." : "Connected"}
                                        </div>
                                        <p className="text-gray-600">Call active with {phoneNumber}</p>
                                    </div>

                                    <div className="rounded-lg bg-gray-50 p-6">
                                        <div className="mb-4 flex items-center justify-center">
                                            <div className="flex h-16 w-16 animate-pulse items-center justify-center rounded-full bg-green-500">
                                                <Mic className="h-8 w-8 text-white" />
                                            </div>
                                        </div>
                                        <p className="text-center text-gray-700">
                                            Speak naturally to ask questions about your documents. The AI will search through your uploaded PDFs and provide
                                            answers.
                                        </p>
                                    </div>

                                    <Button onClick={handleEndCall} className="bg-red-600 hover:bg-red-700" size="lg">
                                        <PhoneOff className="mr-2 h-5 w-5" />
                                        End Call
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Feature Info */}
                    <div className="mt-8 rounded-lg bg-white p-6 shadow">
                        <h3 className="mb-4 text-lg font-semibold text-gray-900">How Voice Calling Works</h3>
                        <div className="grid grid-cols-1 gap-4 text-sm text-gray-600 md:grid-cols-3">
                            <div className="text-center">
                                <PhoneCall className="mx-auto mb-2 h-8 w-8 text-blue-600" />
                                <p>
                                    <strong>Call & Connect</strong>
                                </p>
                                <p>Dial in to start a voice conversation with your AI assistant</p>
                            </div>
                            <div className="text-center">
                                <Mic className="mx-auto mb-2 h-8 w-8 text-green-600" />
                                <p>
                                    <strong>Ask Questions</strong>
                                </p>
                                <p>Speak naturally about your documents and get instant answers</p>
                            </div>
                            <div className="text-center">
                                <Search className="mx-auto mb-2 h-8 w-8 text-purple-600" />
                                <p>
                                    <strong>Smart Search</strong>
                                </p>
                                <p>AI searches through your PDFs and provides relevant information</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Call;
