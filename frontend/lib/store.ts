import { create } from 'zustand'

interface Repository {
  id: number
  name: string
  url: string
  status: string
  total_resources: number
  total_modules: number
  total_variables: number
  providers_count: number
}

interface Store {
  selectedRepository: Repository | null
  setSelectedRepository: (repo: Repository | null) => void
  repositories: Repository[]
  setRepositories: (repos: Repository[]) => void
}

export const useStore = create<Store>((set) => ({
  selectedRepository: null,
  setSelectedRepository: (repo) => set({ selectedRepository: repo }),
  repositories: [],
  setRepositories: (repos) => set({ repositories: repos }),
}))
