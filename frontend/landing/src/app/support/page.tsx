import { redirect } from "next/navigation";

export default function SupportPage() {
    // Redirect to the static application
    redirect("/support/index.html");
}

export async function generateMetadata() {
    return {
        title: "Support Agent Platform",
        description: "Advanced support platform with document management and conversation history"
    };
}
