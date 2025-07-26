import React from "react";
import { cn } from "@/lib/utils";

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  tabs: { id: string; label: string }[];
  className?: string;
}

export function TabNavigation({
  activeTab,
  onTabChange,
  tabs,
  className,
}: TabNavigationProps) {
  return (
    <div className={cn("flex space-x-1 rounded-lg bg-gray-200 p-1", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-all",
            activeTab === tab.id
              ? "bg-white text-purple-700 shadow-sm"
              : "text-gray-600 hover:bg-gray-300 hover:text-gray-900"
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
} 