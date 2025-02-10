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

  async chat(message: string, tools?: string[]): Promise<ReadableStream<string>> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ message, tools }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    return response.body;
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