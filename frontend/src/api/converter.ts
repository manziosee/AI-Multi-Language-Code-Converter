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
  async convertCode(request: ConversionRequest): Promise<ConversionResponse> {
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
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
