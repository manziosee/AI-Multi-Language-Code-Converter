import axios from 'axios';
import type { ConversionRequest, ConversionResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const converterApi = {
  /**
   * Convert code from one language to another
   */
  async convertCode(request: ConversionRequest & { auto_format?: boolean; include_analysis?: boolean }): Promise<ConversionResponse> {
    const response = await apiClient.post<ConversionResponse>('/convert', request);
    return response.data;
  },

  /**
   * Convert code with streaming response
   */
  async convertCodeStream(
    request: ConversionRequest, 
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/convert/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Conversion failed: ${errorText || response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) throw new Error('Stream not available');

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } finally {
      reader.releaseLock();
    }
  },

  /**
   * Convert code from an uploaded file
   */
  async convertFile(
    file: File,
    sourceLanguage: string,
    targetLanguage: string
  ): Promise<ConversionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_language', sourceLanguage);
    formData.append('target_language', targetLanguage);

    const response = await apiClient.post<ConversionResponse>('/convert-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Explain code
   */
  async explainCode(request: { language: string; code: string }): Promise<{ explanation: string; language: string; success: boolean }> {
    const response = await apiClient.post('/explain', request);
    return response.data;
  },

  /**
   * Analyze code for complexity, performance, and security
   */
  async analyzeCode(request: { language: string; code: string }): Promise<any> {
    const response = await apiClient.post('/analyze', request);
    return response.data;
  },

  /**
   * Execute code in sandbox
   */
  async executeCode(request: { language: string; code: string }): Promise<{ success: boolean; output: string; error: string }> {
    const response = await apiClient.post('/execute', request);
    return response.data;
  },

  /**
   * Batch convert multiple files
   */
  async batchConvert(request: { files: Array<{ name: string; code: string }>; source_language: string; target_language: string }): Promise<any> {
    const response = await apiClient.post('/batch-convert', request);
    return response.data;
  },

  /**
   * Format code
   */
  async formatCode(request: { language: string; code: string }): Promise<{ formatted_code: string; success: boolean }> {
    const response = await apiClient.post('/format', request);
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
