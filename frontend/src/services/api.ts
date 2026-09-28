import axios from 'axios';
import type { Work, WorksSummary, WorksListResponse, FilterOptions, SystemStatus, DetectorCoverage } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FetchWorksParams {
  page?: number;
  skip?: number;
  limit?: number;
  search?: string;
  state?: string;
  status?: string;
  financial_year?: string;
  min_amount?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  envelope?: boolean;
}

export const fetchWorks = async (params: FetchWorksParams = {}): Promise<WorksListResponse> => {
  try {
    const response = await apiClient.get<any>('/api/works/', {
      params: {
        envelope: true,
        ...params,
      },
    });
    // In case backend returns raw array or envelope
    if (Array.isArray(response.data)) {
      return {
        total: response.data.length,
        page: params.page || 1,
        limit: params.limit || response.data.length,
        total_pages: 1,
        items: response.data,
      };
    }
    return response.data;
  } catch (error) {
    console.error('Error fetching works:', error);
    throw error;
  }
};

export const fetchWorksSummary = async (): Promise<WorksSummary> => {
  try {
    const response = await apiClient.get<WorksSummary>('/api/works/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching works summary:', error);
    throw error;
  }
};

export const fetchFilterOptions = async (): Promise<FilterOptions> => {
  try {
    const response = await apiClient.get<FilterOptions>('/api/works/filters');
    return response.data;
  } catch (error) {
    console.error('Error fetching filter options:', error);
    return { states: [], statuses: [], financial_years: [] };
  }
};

export const fetchWorkById = async (workId: string): Promise<Work> => {
  try {
    const response = await apiClient.get<Work>(`/api/works/${encodeURIComponent(workId)}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching work ${workId}:`, error);
    throw error;
  }
};

export const fetchCoverage = async (): Promise<DetectorCoverage | null> => {
  try {
    const response = await apiClient.get<DetectorCoverage>('/coverage');
    return response.data;
  } catch (error) {
    console.error('Error fetching coverage:', error);
    return null;
  }
};

export const fetchStatus = async (): Promise<SystemStatus | null> => {
  try {
    const response = await apiClient.get<SystemStatus>('/status');
    return response.data;
  } catch (error) {
    console.error('Error fetching status:', error);
    return null;
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
};
