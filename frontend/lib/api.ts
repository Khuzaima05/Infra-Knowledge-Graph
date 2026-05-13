import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analysisApi = {
  analyzeRepository: (url: string, branch: string = 'main') =>
    apiClient.post('/api/analysis', { url, branch }),
  
  getAnalysisStatus: (repoId: number) =>
    apiClient.get(`/api/analysis/${repoId}/status`),
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

export default apiClient
