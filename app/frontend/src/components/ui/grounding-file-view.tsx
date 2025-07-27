import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

import { Button } from "./button";
import { GroundingFile } from "@/types";

type Properties = {
    groundingFile: GroundingFile | null;
    onClosed: () => void;
};

export default function GroundingFileView({ groundingFile, onClosed }: Properties) {
    return (
        <AnimatePresence>
            {groundingFile && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-2 sm:p-4"
                    onClick={() => onClosed()}
                >
                    <motion.div
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        className="flex max-h-[95vh] sm:max-h-[90vh] w-full max-w-xs sm:max-w-md md:max-w-lg lg:max-w-2xl flex-col rounded-lg bg-card p-3 sm:p-6"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="mb-2 sm:mb-4 flex items-center justify-between">
                            <h2 className="text-base sm:text-xl font-bold text-foreground truncate pr-2">{groundingFile.name}</h2>
                            <Button
                                aria-label="Close grounding file view"
                                variant="ghost"
                                size="sm"
                                className="text-muted-foreground hover:text-foreground flex-shrink-0"
                                onClick={() => onClosed()}
                            >
                                <X className="h-5 w-5" />
                            </Button>
                        </div>
                        <div className="flex-grow overflow-hidden">
                            <pre className="h-[50vh] sm:h-[40vh] overflow-auto text-wrap rounded-md bg-muted p-2 sm:p-4 text-xs sm:text-sm text-muted-foreground">
                                <code>{groundingFile.content}</code>
                            </pre>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
