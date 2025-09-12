import { redirect } from "next/navigation";

export default function AISearchPage() {
    // Redirect to the static application
    redirect("/aisearch/index.html");
}

export async function generateMetadata() {
    return {
        title: "AI Search VoiceRAG",
        description: "Intelligent document search with voice AI"
    };
}
