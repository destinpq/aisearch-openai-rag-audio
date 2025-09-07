import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { useEffect, useRef } from "react";

import { Button } from "./button";
import { GroundingFile } from "@/types";

type Properties = {
    groundingFile: GroundingFile | null;
    onClosed: () => void;
};

export default function GroundingFileView({ groundingFile, onClosed }: Properties) {
    const contentRef = useRef<HTMLPreElement>(null);

    useEffect(() => {
        if (groundingFile?.highlightLine && contentRef.current) {
            // Scroll to the highlighted line
            const lineElements = contentRef.current.querySelectorAll(".content-line");
            const targetLine = lineElements[groundingFile.highlightLine - 1];
            if (targetLine) {
                targetLine.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        }
    }, [groundingFile]);

    const renderContentWithHighlight = (content: string, highlightLine?: number, highlightText?: string) => {
        const lines = content.split("\n");

        return lines.map((line, index) => {
            const lineNumber = index + 1;
            const isHighlighted = highlightLine === lineNumber;
            const isNearHighlight = highlightLine ? Math.abs(lineNumber - highlightLine) <= 2 : false;
            const isFarFromHighlight = highlightLine ? Math.abs(lineNumber - highlightLine) > 2 : false;

            return (
                <div
                    key={index}
                    className={`content-line relative transition-all duration-300 ${
                        isHighlighted
                            ? "border-l-4 border-yellow-500 bg-yellow-200 pl-2 font-semibold shadow-md"
                            : isNearHighlight
                              ? "bg-yellow-50"
                              : isFarFromHighlight && highlightLine
                                ? "opacity-40 blur-[0.5px]"
                                : ""
                    }`}
                >
                    <span className="mr-2 inline-block w-8 text-xs text-gray-400">{lineNumber}</span>
                    <span className={isHighlighted ? "text-yellow-800" : ""}>
                        {highlightText && line.includes(highlightText) && isHighlighted
                            ? line.split(highlightText).map((part, i) => (
                                  <span key={i}>
                                      {part}
                                      {i < line.split(highlightText).length - 1 && <mark className="rounded bg-yellow-400 px-1">{highlightText}</mark>}
                                  </span>
                              ))
                            : line}
                    </span>
                </div>
            );
        });
    };

    return (
        <AnimatePresence>
            {groundingFile && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
                    onClick={() => onClosed()}
                >
                    <motion.div
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        className="flex max-h-[90vh] w-full max-w-4xl flex-col rounded-lg bg-white p-6"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="mb-4 flex items-center justify-between">
                            <div>
                                <h2 className="text-xl font-bold">{groundingFile.name}</h2>
                                {groundingFile.highlightLine && (
                                    <p className="text-sm text-gray-600">
                                        📍 Highlighted: Line {groundingFile.highlightLine}
                                        {groundingFile.highlightText && ` • "${groundingFile.highlightText}"`}
                                    </p>
                                )}
                            </div>
                            <Button
                                aria-label="Close grounding file view"
                                variant="ghost"
                                size="sm"
                                className="text-gray-500 hover:text-gray-700"
                                onClick={() => onClosed()}
                            >
                                <X className="h-5 w-5" />
                            </Button>
                        </div>
                        <div className="flex-grow overflow-hidden">
                            <pre
                                ref={contentRef}
                                className="h-[60vh] overflow-auto text-wrap rounded-md border bg-gray-50 p-4 font-mono text-sm leading-relaxed"
                            >
                                <code>{renderContentWithHighlight(groundingFile.content, groundingFile.highlightLine, groundingFile.highlightText)}</code>
                            </pre>
                        </div>
                        {groundingFile.highlightLine && (
                            <div className="mt-3 text-center text-xs text-gray-500">
                                💡 The highlighted line contains the information relevant to your query
                            </div>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
