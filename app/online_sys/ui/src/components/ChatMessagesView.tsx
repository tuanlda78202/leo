import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline";
import { Copy, Loader2 } from "lucide-react";
import { ReactNode, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExecutionStep } from "@/lib/api";
import { InputForm } from "@/components/InputForm";
import type React from "react";
import ReactMarkdown from "react-markdown";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  type: 'human' | 'ai';
  content: string;
}

// Markdown component props type
type MdComponentProps = {
  className?: string;
  children?: ReactNode;
  [key: string]: any;
};

const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-border pl-4 italic my-3 text-sm",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-muted rounded px-1 py-0.5 font-mono text-xs",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-muted p-3 rounded-lg overflow-x-auto font-mono text-xs my-3",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-border my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-border px-3 py-2 text-left font-bold",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn("border border-border px-3 py-2", className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  return (
    <div className="text-accent-foreground rounded-3xl break-words min-h-7 bg-accent max-w-[100%] sm:max-w-[90%] px-4 pt-3 rounded-br-lg border border-border">
      <ReactMarkdown components={mdComponents}>
        {message.content}
      </ReactMarkdown>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: Message;
  historicalActivity: ProcessedEvent[] | undefined;
  historicalTotalTime: number | undefined;
  liveActivity: ProcessedEvent[] | undefined;
  isLastMessage: boolean;
  isOverallLoading: boolean;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  historicalActivity,
  historicalTotalTime,
  liveActivity,
  isLastMessage,
  isOverallLoading,
  mdComponents,
  handleCopy,
  copiedMessageId,
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime, setStartTime] = useState<number | null>(null);

  // Timer logic for live activity
  const isLiveActivityForThisBubble = isLastMessage && isOverallLoading;

  useEffect(() => {
    if (isLiveActivityForThisBubble && !startTime) {
      setStartTime(Date.now());
      setElapsedTime(0);
    } else if (!isLiveActivityForThisBubble) {
      setStartTime(null);
      setElapsedTime(0);
    }
  }, [isLiveActivityForThisBubble, startTime]);

  useEffect(() => {
    if (!isLiveActivityForThisBubble || !startTime) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const elapsed = (now - startTime) / 1000;
      setElapsedTime(elapsed);
    }, 100);

    return () => clearInterval(interval);
  }, [isLiveActivityForThisBubble, startTime]);

  // Determine which activity events to show
  const activityForThisBubble =
    isLastMessage && isOverallLoading ? liveActivity : historicalActivity;

  return (
    <div className="relative break-words flex flex-col w-full">
      {activityForThisBubble && activityForThisBubble.length > 0 && (
        <div className="mb-3">
          <ActivityTimeline
            processedEvents={activityForThisBubble}
            isLoading={isLiveActivityForThisBubble}
            thinkingTime={isLiveActivityForThisBubble ? elapsedTime : undefined}
            totalCompletedTime={!isLiveActivityForThisBubble ? historicalTotalTime : undefined}
          />
        </div>
      )}

      <div className="prose prose-sm max-w-none text-foreground">
        <ReactMarkdown components={mdComponents}>
          {message.content}
        </ReactMarkdown>
      </div>

      {/* Simple copy button below response, left aligned like ChatGPT */}
      <div className="flex items-center gap-2 mt-3">
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground hover:text-foreground hover:bg-accent p-1 h-8 w-8"
          onClick={() => handleCopy(message.content, message.id)}
        >
          <Copy className="h-4 w-4" />
        </Button>
        {copiedMessageId === message.id && (
          <span className="text-xs text-muted-foreground">Copied!</span>
        )}
      </div>
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  onSubmit: (inputValue: string) => void;
  onCancel: () => void;
  liveActivityEvents?: ProcessedEvent[];
  liveExecutionSteps?: ExecutionStep[];
  historicalActivities?: Record<string, ProcessedEvent[]>;
  historicalTotalTimes?: Record<string, number>;
  error?: string | null;
}

export function ChatMessagesView({
  messages,
  isLoading,
  onSubmit,
  onCancel,
  liveActivityEvents = [],
  historicalActivities = {},
  historicalTotalTimes = {},
  error,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime, setStartTime] = useState<number | null>(null);

  // Timer logic for initial loading
  useEffect(() => {
    if (isLoading && !startTime) {
      setStartTime(Date.now());
      setElapsedTime(0);
    } else if (!isLoading) {
      setStartTime(null);
      setElapsedTime(0);
    }
  }, [isLoading, startTime]);

  useEffect(() => {
    if (!isLoading || !startTime) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const elapsed = (now - startTime) / 1000;
      setElapsedTime(elapsed);
    }, 100);

    return () => clearInterval(interval);
  }, [isLoading, startTime]);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-grow">
        <div className="p-4 md:p-6 space-y-6 max-w-4xl mx-auto pt-4">
          {messages.map((message, index) => {
            const isLast = index === messages.length - 1;
            return (
              <div key={message.id || `msg-${index}`} className="space-y-3">
                <div
                  className={`flex items-start gap-3 ${message.type === "human" ? "justify-end" : ""
                    }`}
                >
                  {message.type === "human" ? (
                    <HumanMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                    />
                  ) : (
                    <AiMessageBubble
                      message={message}
                      historicalActivity={historicalActivities[message.id]}
                      historicalTotalTime={historicalTotalTimes[message.id]}
                      liveActivity={liveActivityEvents}
                      isLastMessage={isLast}
                      isOverallLoading={isLoading}
                      mdComponents={mdComponents}
                      handleCopy={handleCopy}
                      copiedMessageId={copiedMessageId}
                    />
                  )}
                </div>
              </div>
            );
          })}

          {error && (
            <div className="flex items-start gap-3 mt-3">
              <div className="relative group max-w-[85%] md:max-w-[80%] rounded-xl p-3 shadow-sm break-words bg-destructive text-destructive-foreground rounded-bl-none w-full">
                <strong>Error:</strong> {error}
              </div>
            </div>
          )}

          {isLoading &&
            (messages.length === 0 ||
              messages[messages.length - 1].type === "human") && (
              <div className="w-full">
                {liveActivityEvents.length > 0 ? (
                  <ActivityTimeline
                    processedEvents={liveActivityEvents}
                    isLoading={true}
                    thinkingTime={elapsedTime}
                    totalCompletedTime={undefined}
                  />
                ) : (
                  <div className="flex items-center justify-between p-6 bg-card rounded-xl border">
                    <div className="flex items-center">
                      <Loader2 className="h-5 w-5 animate-spin text-muted-foreground mr-2" />
                      <span className="text-card-foreground">Leo is thinking...</span>
                    </div>
                    <span className="text-muted-foreground text-sm font-mono">
                      {elapsedTime.toFixed(1)}s
                    </span>
                  </div>
                )}
              </div>
            )}
        </div>
      </ScrollArea>
      <InputForm
        onSubmit={onSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={messages.length > 0}
      />
    </div>
  );
}
