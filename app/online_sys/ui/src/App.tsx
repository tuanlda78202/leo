import { APIError, ExecutionStep, api } from "@/lib/api";
import { useCallback, useState } from "react";

import { ChatMessagesView } from "@/components/ChatMessagesView";
import { Header } from "@/components/Header";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { ThemeProvider } from "@/lib/theme";
import { WelcomeScreen } from "@/components/WelcomeScreen";

interface Message {
  id: string;
  type: 'human' | 'ai';
  content: string;
  timestamp?: number;
}

// Convert backend execution steps to frontend ProcessedEvent format
const convertExecutionStepsToEvents = (steps: ExecutionStep[]): ProcessedEvent[] => {
  return steps.map(step => ({
    title: step.title,
    data: step.description + (step.duration ? ` (${step.duration.toFixed(2)}s)` : '')
  }));
};

function AppContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveActivityEvents, setLiveActivityEvents] = useState<ProcessedEvent[]>([]);
  const [historicalActivities, setHistoricalActivities] = useState<Record<string, ProcessedEvent[]>>({});

  const handleSubmit = useCallback(async (
    inputValue: string,
    _effort: string,
    _model: string
  ) => {
    if (!inputValue.trim()) return;

    setIsLoading(true);
    setError(null);
    setLiveActivityEvents([]);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'human',
      content: inputValue,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const steps: ExecutionStep[] = [];
      let finalResult = '';

      // Stream the agent execution
      for await (const event of api.chatStream(inputValue)) {
        console.log('Received stream event:', event);

        if (event.type === 'step') {
          const step = event.data as ExecutionStep;
          steps.push(step);

          // Update live activity events
          const processedEvents = convertExecutionStepsToEvents(steps);
          setLiveActivityEvents(processedEvents);

        } else if (event.type === 'result') {
          const response = event.data;
          finalResult = response.result;

        } else if (event.type === 'error') {
          setError(event.data.error || 'Unknown error occurred');
          setLiveActivityEvents([]);
          setIsLoading(false);
          return;

        } else if (event.type === 'done') {
          break;
        }
      }

      if (finalResult) {
        // Add AI response
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: finalResult,
          timestamp: Date.now(),
        };

        setMessages(prev => [...prev, aiMessage]);

        // Save historical activity for this message
        if (steps.length > 0) {
          const processedEvents = convertExecutionStepsToEvents(steps);
          setHistoricalActivities(prev => ({
            ...prev,
            [aiMessage.id]: processedEvents
          }));
        }

        // Clear live events
        setLiveActivityEvents([]);
      }
    } catch (err) {
      console.error('API call failed:', err);
      if (err instanceof APIError) {
        setError(`API Error: ${err.message}`);
      } else {
        setError('Failed to connect to the API');
      }
      setLiveActivityEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleCancel = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setLiveActivityEvents([]);
  }, []);

  return (
    <div className="flex h-screen bg-background text-foreground font-sans antialiased">
      {/* Fixed positioned header icons */}
      <Header hasHistory={messages.length > 0} />

      <main className="flex-1 flex flex-col overflow-hidden max-w-4xl mx-auto w-full">
        <div className={`flex-1 overflow-y-auto ${messages.length === 0 ? "flex" : ""}`}>
          {messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={isLoading}
              onCancel={handleCancel}
            />
          ) : (
            <ChatMessagesView
              messages={messages}
              isLoading={isLoading}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={liveActivityEvents}
              historicalActivities={historicalActivities}
              error={error}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="leo-ui-theme">
      <AppContent />
    </ThemeProvider>
  );
}
