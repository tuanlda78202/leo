// API configuration and service functions for connecting to FastAPI backend

const API_BASE_URL = import.meta.env.DEV
  ? '/api' // Use proxy in development
  : '/api'; // Use nginx proxy in production too

// Get API key from environment variables
const API_KEY = import.meta.env.VITE_LEO_API_KEY;

// WebSocket URL - construct properly for different environments
const WS_BASE_URL = (() => {
  if (import.meta.env.DEV) {
    // Development: construct WebSocket URL from current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/api`;
  } else {
    // Production: same logic
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/api`;
  }
})();

interface ChatRequest {
  task: string;
}

interface ExecutionStep {
  step_number: number;
  title: string;
  description: string;
  tool_name?: string;
  tool_args?: Record<string, any>;
  duration?: number;
  input_tokens?: number;
  output_tokens?: number;
  timestamp?: number;
}

interface ChatResponse {
  result: string;
  success: boolean;
  error?: string;
  execution_steps?: ExecutionStep[];
}

interface StreamEvent {
  type: 'step' | 'result' | 'error' | 'done' | 'auth_success' | 'auth_error' | 'cancelled';
  data?: any;
}

interface HealthResponse {
  status: string;
  service: string;
  agent_name: string;
  agent_max_steps: number;
}

class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

async function makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add API key if available
  if (API_KEY) {
    defaultHeaders['Leo-API-Key'] = API_KEY;
    console.log('API Key found:', API_KEY.substring(0, 8) + '...');
  } else {
    console.warn('No API key found in environment variables');
  }

  console.log('Making request to:', url);
  console.log('With headers:', defaultHeaders);
  console.log('With options:', options);

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  console.log('Response status:', response.status);
  console.log('Response headers:', response.headers);

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Response error:', errorText);
    throw new APIError(
      `HTTP ${response.status}: ${errorText}`,
      response.status
    );
  }

  const data = await response.json();
  console.log('Response data:', data);
  return data;
}

// Streaming chat function using SSE
async function* streamChat(task: string): AsyncGenerator<StreamEvent, void, unknown> {
  const url = `${API_BASE_URL}/v1/chat/stream`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (API_KEY) {
    headers['Leo-API-Key'] = API_KEY;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({ task }),
  });

  if (!response.ok) {
    throw new APIError(`HTTP ${response.status}`, response.status);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new APIError('Failed to get response reader');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const eventData = JSON.parse(line.slice(6));
            yield eventData as StreamEvent;

            if (eventData.type === 'done') {
              return;
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// WebSocket-based streaming chat
class WebSocketChat {
  private ws: WebSocket | null = null;
  private eventHandlers: Map<string, (event: StreamEvent) => void> = new Map();
  private isConnected = false;
  private isAuthenticated = false;

  constructor() { }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      // Note: backend WebSocket endpoint is /ws/chat, so with nginx proxy it becomes /api/ws/chat
      const wsUrl = `${WS_BASE_URL}/ws/chat`;
      console.log('Connecting to WebSocket:', wsUrl);

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.authenticate().then(() => resolve()).catch(reject);
      };

      this.ws.onmessage = (event) => {
        try {
          const message: StreamEvent = JSON.parse(event.data);
          console.log('WebSocket message received:', message);

          // Handle authentication
          if (message.type === 'auth_success') {
            this.isAuthenticated = true;
            console.log('WebSocket authenticated');
          } else if (message.type === 'auth_error') {
            this.isAuthenticated = false;
            console.error('WebSocket authentication failed');
          }

          // Call registered event handlers
          const handler = this.eventHandlers.get('message');
          if (handler) {
            handler(message);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.isAuthenticated = false;
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new APIError('WebSocket connection failed'));
      };
    });
  }

  private async authenticate(): Promise<void> {
    if (!this.ws || !API_KEY) {
      throw new APIError('No API key available for WebSocket authentication');
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new APIError('Authentication timeout'));
      }, 5000);

      const originalHandler = this.eventHandlers.get('message');

      this.eventHandlers.set('message', (event: StreamEvent) => {
        if (event.type === 'auth_success') {
          clearTimeout(timeout);
          this.eventHandlers.set('message', originalHandler || (() => { }));
          resolve();
        } else if (event.type === 'auth_error') {
          clearTimeout(timeout);
          this.eventHandlers.set('message', originalHandler || (() => { }));
          reject(new APIError('Authentication failed'));
        }

        // Still call original handler for other messages
        if (originalHandler && event.type !== 'auth_success' && event.type !== 'auth_error') {
          originalHandler(event);
        }
      });

      this.send({
        type: 'auth',
        data: { api_key: API_KEY }
      });
    });
  }

  onMessage(handler: (event: StreamEvent) => void): void {
    this.eventHandlers.set('message', handler);
  }

  async sendTask(task: string): Promise<void> {
    if (!this.isConnected || !this.isAuthenticated) {
      throw new APIError('WebSocket not connected or authenticated');
    }

    this.send({
      type: 'task',
      data: { task }
    });
  }

  async cancelTask(): Promise<void> {
    if (!this.isConnected || !this.isAuthenticated) {
      throw new APIError('WebSocket not connected or authenticated');
    }

    this.send({
      type: 'cancel'
    });
  }

  private send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      throw new APIError('WebSocket not connected');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.isAuthenticated = false;
  }
}

// WebSocket streaming generator that works with existing code
async function* streamChatWebSocket(task: string): AsyncGenerator<StreamEvent, void, unknown> {
  const wsChat = new WebSocketChat();

  try {
    await wsChat.connect();

    // Create a promise-based event system
    const events: StreamEvent[] = [];
    let isComplete = false;
    let error: Error | null = null;

    wsChat.onMessage((event: StreamEvent) => {
      events.push(event);

      if (event.type === 'done' || event.type === 'error') {
        isComplete = true;
      }

      if (event.type === 'error') {
        error = new APIError(event.data?.message || 'WebSocket error');
      }
    });

    // Send the task
    await wsChat.sendTask(task);

    // Yield events as they come in
    let lastIndex = 0;

    while (!isComplete && !error) {
      // Yield any new events
      for (let i = lastIndex; i < events.length; i++) {
        yield events[i];

        if (events[i].type === 'done' || events[i].type === 'error') {
          return;
        }
      }
      lastIndex = events.length;

      // Wait a bit before checking for new events
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    if (error) {
      throw error;
    }

  } finally {
    wsChat.disconnect();
  }
}

export const api = {
  // Regular chat (non-streaming)
  chat: async (task: string): Promise<ChatResponse> => {
    console.log('Calling chat API with task:', task);
    return makeRequest<ChatResponse>('/v1/chat', {
      method: 'POST',
      body: JSON.stringify({ task }),
    });
  },

  // Streaming chat (SSE)
  chatStream: streamChat,

  // Streaming chat (WebSocket)
  chatStreamWS: streamChatWebSocket,

  // WebSocket class for advanced usage
  WebSocketChat,

  // Health check
  health: async (): Promise<HealthResponse> => {
    return makeRequest<HealthResponse>('/health');
  },

  // Basic connectivity check
  ping: async (): Promise<{ message: string }> => {
    return makeRequest<{ message: string }>('/');
  },
};

export { APIError };
export type { ChatRequest, ChatResponse, HealthResponse, ExecutionStep, StreamEvent };