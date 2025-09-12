import React, { useState } from "react";
import { Phone, PhoneOff, PhoneCall } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CallInterfaceProps {
    onCallInitiated?: (callSid: string) => void;
    onCallEnded?: () => void;
}

interface CallStatus {
    call_sid?: string;
    status?: string;
    duration?: string;
    error?: string;
}

const CallInterface: React.FC<CallInterfaceProps> = ({ onCallInitiated, onCallEnded }) => {
    const [phoneNumber, setPhoneNumber] = useState("");
    const [isCalling, setIsCalling] = useState(false);
    const [callStatus, setCallStatus] = useState<CallStatus | null>(null);
    const [error, setError] = useState<string | null>(null);

    const formatPhoneNumber = (value: string) => {
        // Remove all non-numeric characters
        const cleaned = value.replace(/\D/g, "");

        // Format as +1 (XXX) XXX-XXXX for US numbers
        if (cleaned.length >= 10) {
            return `+${cleaned.slice(0, 1)} (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 11)}`;
        }

        return cleaned;
    };

    const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const formatted = formatPhoneNumber(e.target.value);
        setPhoneNumber(formatted);
    };

    const initiateCall = async () => {
        if (!phoneNumber) {
            setError("Please enter a phone number");
            return;
        }

        setIsCalling(true);
        setError(null);
        setCallStatus(null);

        try {
            const response = await fetch("/call/initiate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    to_number: phoneNumber.replace(/\D/g, "") // Remove formatting for API
                })
            });

            const result = await response.json();

            if (result.success) {
                setCallStatus({
                    call_sid: result.call_sid,
                    status: result.status
                });
                onCallInitiated?.(result.call_sid);
            } else {
                setError(result.error || "Failed to initiate call");
            }
        } catch (err) {
            setError("Network error occurred");
            console.error("Call initiation error:", err);
        } finally {
            setIsCalling(false);
        }
    };

    const endCall = async () => {
        if (!callStatus?.call_sid) return;

        try {
            const response = await fetch(`/call/end/${callStatus.call_sid}`, {
                method: "POST"
            });

            const result = await response.json();

            if (result.success) {
                setCallStatus(null);
                onCallEnded?.();
            } else {
                setError(result.error || "Failed to end call");
            }
        } catch (err) {
            setError("Network error occurred");
            console.error("Call ending error:", err);
        }
    };

    const getStatusColor = (status?: string) => {
        switch (status?.toLowerCase()) {
            case "in-progress":
                return "text-green-600";
            case "completed":
                return "text-blue-600";
            case "failed":
            case "busy":
            case "no-answer":
                return "text-red-600";
            default:
                return "text-gray-600";
        }
    };

    return (
        <Card className="mx-auto w-full max-w-md">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <PhoneCall className="h-5 w-5" />
                    Voice Calling
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {!callStatus ? (
                    <>
                        <div className="space-y-2">
                            <label htmlFor="phone" className="text-sm font-medium">
                                Phone Number
                            </label>
                            <input
                                id="phone"
                                type="tel"
                                placeholder="+1 (555) 123-4567"
                                value={phoneNumber}
                                onChange={handlePhoneNumberChange}
                                disabled={isCalling}
                                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <Button onClick={initiateCall} disabled={isCalling || !phoneNumber} className="w-full">
                            {isCalling ? (
                                <>
                                    <Phone className="mr-2 h-4 w-4 animate-pulse" />
                                    Calling...
                                </>
                            ) : (
                                <>
                                    <Phone className="mr-2 h-4 w-4" />
                                    Call AI Assistant
                                </>
                            )}
                        </Button>
                    </>
                ) : (
                    <div className="space-y-4">
                        <div className="text-center">
                            <div className={`text-lg font-semibold ${getStatusColor(callStatus.status)}`}>
                                {callStatus.status === "in-progress"
                                    ? "Call in Progress"
                                    : callStatus.status === "completed"
                                      ? "Call Completed"
                                      : callStatus.status || "Unknown Status"}
                            </div>
                            {callStatus.duration && <div className="text-sm text-gray-600">Duration: {callStatus.duration}s</div>}
                        </div>

                        {callStatus.status === "in-progress" && (
                            <Button onClick={endCall} variant="destructive" className="w-full">
                                <PhoneOff className="mr-2 h-4 w-4" />
                                End Call
                            </Button>
                        )}

                        <Button
                            onClick={() => {
                                setCallStatus(null);
                                setPhoneNumber("");
                                setError(null);
                            }}
                            variant="outline"
                            className="w-full"
                        >
                            New Call
                        </Button>
                    </div>
                )}

                {error && (
                    <div className="rounded-md border border-red-200 bg-red-50 p-4">
                        <div className="text-red-800">{error}</div>
                    </div>
                )}

                <div className="text-center text-xs text-gray-500">The AI assistant will answer questions about your documents and company policies.</div>
            </CardContent>
        </Card>
    );
};

export default CallInterface;
