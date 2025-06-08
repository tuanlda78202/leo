import {
  Activity,
  Brain,
  ChevronDown,
  ChevronUp,
  Info,
  Loader2,
  Pen,
  Search,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { useEffect, useState } from "react";

import { ScrollArea } from "@/components/ui/scroll-area";

export interface ProcessedEvent {
  title: string;
  data: any;
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
  thinkingTime?: number; // Live thinking time when loading
  totalCompletedTime?: number; // Total time when completed
}

export function ActivityTimeline({
  processedEvents,
  isLoading,
  thinkingTime,
  totalCompletedTime,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);

  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className="h-4 w-4 text-muted-foreground animate-spin" />;
    }
    if (title.toLowerCase().includes("web_search") || title.toLowerCase().includes("web search")) {
      return <Search className="h-4 w-4 text-blue-400" />;
    } else if (title.toLowerCase().includes("iam")) {
      return <Info className="h-4 w-4 text-green-400" />;
    } else if (title.toLowerCase().includes("summarizer")) {
      return <Brain className="h-4 w-4 text-purple-400" />;
    } else if (title.toLowerCase().includes("starting")) {
      return <Activity className="h-4 w-4 text-muted-foreground" />;
    } else if (title.toLowerCase().includes("complete")) {
      return <Pen className="h-4 w-4 text-green-400" />;
    }
    return <Activity className="h-4 w-4 text-muted-foreground" />;
  };

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);

  return (
    <Card className="max-h-96">
      <CardHeader>
        <CardDescription className="flex items-center justify-between">
          <div
            className="flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-foreground"
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            <span>Thinking</span>
            {isLoading && thinkingTime !== undefined ? (
              // Show live thinking time while loading
              <span className="font-mono text-muted-foreground">
                {thinkingTime.toFixed(1)}s
              </span>
            ) : !isLoading && totalCompletedTime !== undefined ? (
              // Show total time when completed (remove the > 0 check)
              <span className="font-mono text-muted-foreground">
                {totalCompletedTime.toFixed(1)}s
              </span>
            ) : null}
            {isTimelineCollapsed ? (
              <ChevronDown className="h-4 w-4 mr-2" />
            ) : (
              <ChevronUp className="h-4 w-4 mr-2" />
            )}
          </div>
        </CardDescription>
      </CardHeader>
      {!isTimelineCollapsed && (
        <ScrollArea className="max-h-96 overflow-y-auto">
          <CardContent>
            {isLoading && processedEvents.length === 0 && (
              <div className="relative pl-8 pb-4">
                <div className="absolute left-3 top-3.5 h-full w-0.5 bg-border" />
                <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-muted flex items-center justify-center ring-4 ring-background">
                  <Loader2 className="h-3 w-3 text-muted-foreground animate-spin" />
                </div>
                <div>
                  <p className="text-sm text-foreground font-medium">
                    Searching...
                  </p>
                </div>
              </div>
            )}
            {processedEvents.length > 0 ? (
              <div className="space-y-0">
                {processedEvents.map((eventItem, index) => (
                  <div key={index} className="relative pl-8 pb-4">
                    {index < processedEvents.length - 1 ||
                      (isLoading && index === processedEvents.length - 1) ? (
                      <div className="absolute left-3 top-3.5 h-full w-0.5 bg-border" />
                    ) : null}
                    <div className="absolute left-0.5 top-2 h-6 w-6 rounded-full bg-muted flex items-center justify-center ring-4 ring-background">
                      {getEventIcon(eventItem.title, index)}
                    </div>
                    <div>
                      <p className="text-sm text-foreground font-medium mb-0.5">
                        {eventItem.title}
                      </p>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {typeof eventItem.data === "string"
                          ? eventItem.data
                          : Array.isArray(eventItem.data)
                            ? (eventItem.data as string[]).join(", ")
                            : JSON.stringify(eventItem.data)}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <div className="relative pl-8 pb-4">
                    <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-muted flex items-center justify-center ring-4 ring-background">
                      <Loader2 className="h-3 w-3 text-muted-foreground animate-spin" />
                    </div>
                    <div>
                      <p className="text-sm text-foreground font-medium">
                        Searching...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : !isLoading ? ( // Only show "No activity" if not loading and no events
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground pt-10">
                <Info className="h-6 w-6 mb-3" />
                <p className="text-sm">No activity to display.</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Timeline will update during processing.
                </p>
              </div>
            ) : null}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  );
}
