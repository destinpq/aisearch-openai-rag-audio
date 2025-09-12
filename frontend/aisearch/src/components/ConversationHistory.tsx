import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { History, MessageSquare, Search, Calendar, Clock, Trash2, RefreshCw, Filter } from "lucide-react";
import { Conversation } from "@/types";

interface ConversationHistoryProps {
    onConversationSelect: (conversationId: string) => void;
}

export function ConversationHistory({ onConversationSelect }: ConversationHistoryProps) {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [filteredConversations, setFilteredConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("all");

    useEffect(() => {
        loadConversations();
    }, []);

    useEffect(() => {
        filterConversations();
    }, [conversations, searchTerm, statusFilter]);

    const loadConversations = async () => {
        try {
            setLoading(true);
            const response = await fetch("/api/conversations");
            if (response.ok) {
                const data = await response.json();
                setConversations(data.conversations || []);
            } else {
                console.error("Failed to load conversations");
            }
        } catch (error) {
            console.error("Error loading conversations:", error);
        } finally {
            setLoading(false);
        }
    };

    const filterConversations = () => {
        let filtered = conversations;

        // Apply search filter
        if (searchTerm.trim()) {
            const search = searchTerm.toLowerCase();
            filtered = filtered.filter(conv => conv.title?.toLowerCase().includes(search) || conv.id.toLowerCase().includes(search));
        }

        // Apply status filter
        if (statusFilter !== "all") {
            filtered = filtered.filter(conv => conv.status === statusFilter);
        }

        setFilteredConversations(filtered);
    };

    const handleDeleteConversation = async (conversationId: string) => {
        if (!confirm("Are you sure you want to delete this conversation?")) {
            return;
        }

        try {
            const response = await fetch(`/api/conversations/${conversationId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                setConversations(prev => prev.filter(conv => conv.id !== conversationId));
            } else {
                console.error("Failed to delete conversation");
            }
        } catch (error) {
            console.error("Error deleting conversation:", error);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "active":
                return <Badge className="bg-green-100 text-green-700">Active</Badge>;
            case "completed":
                return <Badge className="bg-blue-100 text-blue-700">Completed</Badge>;
            case "error":
                return <Badge className="bg-red-100 text-red-700">Error</Badge>;
            default:
                return <Badge variant="secondary">{status}</Badge>;
        }
    };

    const getDurationText = (seconds: number) => {
        if (seconds < 60) {
            return `${seconds}s`;
        } else if (seconds < 3600) {
            return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="flex items-center text-2xl font-bold">
                        <History className="mr-2 h-6 w-6" />
                        Conversation History
                    </h2>
                    <p className="text-muted-foreground">View and manage your past conversations</p>
                </div>
                <Button onClick={loadConversations} variant="outline" size="sm">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>

            {/* Search and Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col gap-4 sm:flex-row">
                        <div className="flex-1">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
                                <Input
                                    placeholder="Search conversations..."
                                    value={searchTerm}
                                    onChange={e => setSearchTerm(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Filter className="h-4 w-4 text-muted-foreground" />
                            <select
                                value={statusFilter}
                                onChange={e => setStatusFilter(e.target.value)}
                                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                            >
                                <option value="all">All Status</option>
                                <option value="active">Active</option>
                                <option value="completed">Completed</option>
                                <option value="error">Error</option>
                            </select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Conversations List */}
            <div className="space-y-4">
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                        <span className="ml-2 text-muted-foreground">Loading conversations...</span>
                    </div>
                ) : filteredConversations.length === 0 ? (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <MessageSquare className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
                            <h3 className="mb-2 text-lg font-semibold">No conversations found</h3>
                            <p className="text-muted-foreground">
                                {conversations.length === 0 ? "Start a conversation to see your history here." : "Try adjusting your search or filters."}
                            </p>
                        </CardContent>
                    </Card>
                ) : (
                    <ScrollArea className="h-[600px]">
                        <div className="space-y-3">
                            {filteredConversations.map(conversation => (
                                <Card key={conversation.id} className="transition-shadow hover:shadow-md">
                                    <CardContent className="p-4">
                                        <div className="flex items-start justify-between">
                                            <div className="min-w-0 flex-1">
                                                <div className="mb-2 flex items-center space-x-3">
                                                    <h3 className="truncate font-semibold">
                                                        {conversation.title || `Conversation ${conversation.id.slice(-8)}`}
                                                    </h3>
                                                    {getStatusBadge(conversation.status)}
                                                </div>

                                                <div className="mb-3 flex items-center space-x-4 text-sm text-muted-foreground">
                                                    <div className="flex items-center">
                                                        <Calendar className="mr-1 h-4 w-4" />
                                                        {formatDate(conversation.created_at)}
                                                    </div>
                                                    {conversation.total_messages > 0 && (
                                                        <div className="flex items-center">
                                                            <MessageSquare className="mr-1 h-4 w-4" />
                                                            {conversation.total_messages} messages
                                                        </div>
                                                    )}
                                                    {conversation.duration_seconds > 0 && (
                                                        <div className="flex items-center">
                                                            <Clock className="mr-1 h-4 w-4" />
                                                            {getDurationText(conversation.duration_seconds)}
                                                        </div>
                                                    )}
                                                </div>

                                                <p className="text-sm text-muted-foreground">ID: {conversation.id}</p>
                                            </div>

                                            <div className="ml-4 flex items-center space-x-2">
                                                <Button onClick={() => onConversationSelect(conversation.id)} size="sm" variant="outline">
                                                    View
                                                </Button>
                                                <Button
                                                    onClick={() => handleDeleteConversation(conversation.id)}
                                                    size="sm"
                                                    variant="outline"
                                                    className="text-red-600 hover:text-red-700"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </div>

            {/* Stats */}
            {conversations.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Statistics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-blue-600">{conversations.length}</div>
                                <div className="text-sm text-muted-foreground">Total Conversations</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-green-600">{conversations.filter(c => c.status === "active").length}</div>
                                <div className="text-sm text-muted-foreground">Active</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-blue-600">{conversations.filter(c => c.status === "completed").length}</div>
                                <div className="text-sm text-muted-foreground">Completed</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-red-600">{conversations.reduce((sum, c) => sum + c.total_messages, 0)}</div>
                                <div className="text-sm text-muted-foreground">Total Messages</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
