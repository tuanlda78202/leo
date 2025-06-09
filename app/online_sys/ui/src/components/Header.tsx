import { SquarePen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

interface HeaderProps {
    hasHistory: boolean;
}

export const Header: React.FC<HeaderProps> = ({ hasHistory }) => {
    return (
        <>
            {/* Top left - New chat button (only show when there's history) */}
            {hasHistory && (
                <div className="fixed top-4 left-4 z-10">
                    <Button
                        variant="ghost"
                        className="text-muted-foreground hover:text-foreground hover:bg-accent"
                        onClick={() => window.location.reload()}
                        title="New chat"
                    >
                        <SquarePen size={16} />
                    </Button>
                </div>
            )}

            {/* Top right - Theme toggle (always show) */}
            <div className="fixed top-4 right-4 z-10">
                <ThemeToggle />
            </div>
        </>
    );
};
