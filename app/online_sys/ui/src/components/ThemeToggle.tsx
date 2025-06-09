import { Monitor, Moon, Sun } from 'lucide-react';

import { Button } from '@/components/ui/button';
import React from 'react';
import { useTheme } from '@/lib/theme';

export const ThemeToggle: React.FC = () => {
    const { theme, setTheme } = useTheme();

    const toggleTheme = () => {
        if (theme === 'light') {
            setTheme('dark');
        } else if (theme === 'dark') {
            setTheme('system');
        } else {
            setTheme('light');
        }
    };

    const getIcon = () => {
        switch (theme) {
            case 'light':
                return <Sun size={16} />;
            case 'dark':
                return <Moon size={16} />;
            case 'system':
                return <Monitor size={16} />;
            default:
                return <Sun size={16} />;
        }
    };

    const getTooltip = () => {
        switch (theme) {
            case 'light':
                return 'Switch to dark mode';
            case 'dark':
                return 'Switch to system mode';
            case 'system':
                return 'Switch to light mode';
            default:
                return 'Toggle theme';
        }
    };

    return (
        <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="text-muted-foreground hover:text-foreground hover:bg-accent"
            title={getTooltip()}
        >
            {getIcon()}
        </Button>
    );
};
