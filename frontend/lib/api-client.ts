import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AnalysisStatus {
  repository_id: number
  name: string
  status: 'pending' | 'cloning' | 'parsing' | 'building_graph' | 'generating_summary' | 'completed' | 'failed' | 'analyzing'
  current_step: string
  progress_percentage: number
  error_message?: string
  started_at: string
  completed_at?: string
  analyzed_at?: string
  statistics?: {
    total_resources: number
    total_modules: number
    total_variables: number
    providers_count: number
  }
}

export interface AnalyzeResponse {
  repository_id: number
  message: string
  status: string
  estimated_time_seconds?: number
}

// Extend apiClient with custom methods
const extendedApiClient = Object.assign(apiClient, {
  analyzeRepository: async (data: { url: string; branch?: string; force_refresh?: boolean; async_mode?: boolean }) => {
    const response = await apiClient.post<AnalyzeResponse>('/api/analysis', data)
    return response.data
  },
  
  getAnalysisStatus: async (repoId: number) => {
    const response = await apiClient.get<AnalysisStatus>(`/api/analysis/${repoId}/status`)
    return response.data
  },
})

export const analysisApi = {
  analyzeRepository: (url: string, branch: string = 'main') =>
    apiClient.post<AnalyzeResponse>('/api/analysis', { url, branch }),
  
  getAnalysisStatus: (repoId: number) =>
    apiClient.get<AnalysisStatus>(`/api/analysis/${repoId}/status`),
}

export const repositoryApi = {
  listRepositories: (skip: number = 0, limit: number = 10) =>
    apiClient.get('/api/repositories', { params: { skip, limit } }),
  
  getRepository: (repoId: number) =>
    apiClient.get(`/api/repositories/${repoId}`),
  
  getModules: (repoId: number) =>
    apiClient.get(`/api/repositories/${repoId}/modules`),
  
  getResources: (repoId: number) =>
    apiClient.get(`/api/repositories/${repoId}/resources`),
  
  getVariables: (repoId: number) =>
    apiClient.get(`/api/repositories/${repoId}/variables`),
  
  getProviders: (repoId: number) =>
    apiClient.get(`/api/repositories/${repoId}/providers`),
}

export const graphApi = {
  getDependencyGraph: (repoId: number) =>
    apiClient.get(`/api/graphs/${repoId}/dependency-graph`),
  
  getArchitectureSummary: (repoId: number) =>
    apiClient.get(`/api/graphs/${repoId}/summary`),
}

export { extendedApiClient as apiClient }
export default extendedApiClient

// Made with Bob
