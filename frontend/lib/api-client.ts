const API_BASE_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  status: string;
  data: T;
}

export interface ChatMessage {
  message: string;
  tools?: string[];
}

export interface SearchRequest {
  query: string;
  max_results?: number;
  search_depth?: string;
}

export interface DocumentSearchRequest {
  query: string;
  k?: number;
  threshold?: number;
}

export interface FREDRequest {
  series_id: string;
  observation_start?: string;
  observation_end?: string;
  units?: string;
}

export interface MarketAnalysisRequest {
  location: string;
  property_type: string;
  analysis_type?: string;
}

export interface PropertyAnalysisRequest {
  property_id: string;
  analysis_type?: string;
}

export interface ValuePropositionRequest {
  property_details: Record<string, any>;
  target_audience?: string;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  uploaded_at: string;
  status: 'processing' | 'completed' | 'failed';
  vector_count?: number;
  error?: string;
}

class ApiClient {
  private ws: WebSocket | null = null;
  private messageCallbacks: Map<string, (message: string) => void> = new Map();

  private getWebSocketUrl(): string {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return baseUrl.replace(/^http(s)?:/, wsProtocol) + '/ws/chat';
  }

  private ensureWebSocketConnection(): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve(this.ws);
        return;
      }

      this.ws = new WebSocket(this.getWebSocketUrl());

      this.ws.onmessage = (event) => {
        const data = event.data;
        // Handle incoming messages and route them to the appropriate callback
        this.messageCallbacks.forEach((callback) => callback(data));
      };

      this.ws.onopen = () => resolve(this.ws!);
      this.ws.onerror = (error) => reject(error);
      this.ws.onclose = () => {
        this.ws = null;
        // Implement reconnection logic here if needed
      };
    });
  }

  async chat(message: string, tools?: string[]): Promise<ReadableStream<string>> {
    const ws = await this.ensureWebSocketConnection();

    // Create a ReadableStream that will receive WebSocket messages
    return new ReadableStream({
      start: (controller) => {
        const messageHandler = (data: string) => {
          if (data === '[DONE]') {
            controller.close();
            this.messageCallbacks.delete(message);
          } else if (data.startsWith('ERROR:')) {
            controller.error(new Error(data.slice(6)));
            this.messageCallbacks.delete(message);
          } else {
            controller.enqueue(data);
          }
        };

        // Store the callback for this message
        this.messageCallbacks.set(message, messageHandler);

        // Send the message through WebSocket
        ws.send(JSON.stringify({ message, tools }));
      },
      cancel: () => {
        this.messageCallbacks.delete(message);
      }
    });
  }

  private async fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const defaultHeaders: HeadersInit = options.body instanceof FormData
      ? { 'Accept': 'application/json' }
      : { 'Content-Type': 'application/json', 'Accept': 'application/json' };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'An error occurred');
    }

    const result = await response.json();
    if (result.status !== 'success') {
      throw new Error(result.detail || 'Operation failed');
    }

    return result;
  }

  async search(request: SearchRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async getEconomicData(request: FREDRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/economic-data', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async analyzeMarket(request: MarketAnalysisRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/market-analysis', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async analyzeProperty(request: PropertyAnalysisRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/property-analysis', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async generateValueProposition(request: ValuePropositionRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/value-proposition', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async documentSearch(request: DocumentSearchRequest): Promise<any> {
    const response = await this.fetchApi<any>('/tools/document-search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.data;
  }

  async listDocuments(): Promise<Document[]> {
    const response = await this.fetchApi<Document[]>('/admin/documents', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    return response.data;
  }

  async uploadDocument(formData: FormData): Promise<Document> {
    const response = await this.fetchApi<Document>('/admin/documents/upload', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
      body: formData,
    });
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    const response = await this.fetchApi<void>(`/admin/documents/${documentId}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient(); 