import axios from 'axios';
import type { Work, SystemStatus, DetectorCoverage } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchWorks = async (params: { skip?: number; limit?: number } = {}): Promise<Work[]> => {
  try {
    const response = await apiClient.get<Work[]>('/api/works/', { params });
    return response.data || [];
  } catch (error) {
    console.error('Error fetching works:', error);
    throw error;
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
