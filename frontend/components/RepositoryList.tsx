'use client'

import { useEffect } from 'react'
import Link from 'next/link'

interface Repository {
  id: number
  name: string
  url: string
  status: string
  total_resources: number
  total_modules: number
  total_variables: number
  providers_count: number
  analyzed_at: string
}

interface Props {
  repositories: Repository[]
  isLoading: boolean
  onLoad: () => void
}

export default function RepositoryList({ repositories, isLoading, onLoad }: Props) {
  useEffect(() => {
    onLoad()
  }, [onLoad])

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin">
          <div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full"></div>
        </div>
        <p className="text-slate-400 mt-4">Loading repositories...</p>
      </div>
    )
  }

  if (repositories.length === 0) {
    return (
      <div className="text-center py-12 bg-card border border-slate-700 rounded-lg">
        <p className="text-slate-400">No repositories analyzed yet. Start by submitting a Terraform repository URL above.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-6">
      <h2 className="text-2xl font-bold text-white">Analyzed Repositories</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {repositories.map((repo) => (
          <div
            key={repo.id}
            className="bg-card border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">{repo.name}</h3>
                <p className="text-xs text-slate-500 truncate">{repo.url}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                repo.status === 'completed'
                  ? 'bg-green-900 text-green-200'
                  : repo.status === 'failed'
                  ? 'bg-red-900 text-red-200'
                  : 'bg-yellow-900 text-yellow-200'
              }`}>
                {repo.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
              <div>
                <p className="text-slate-400">Resources</p>
                <p className="text-2xl font-bold text-blue-400">{repo.total_resources}</p>
              </div>
              <div>
                <p className="text-slate-400">Modules</p>
                <p className="text-2xl font-bold text-purple-400">{repo.total_modules}</p>
              </div>
              <div>
                <p className="text-slate-400">Variables</p>
                <p className="text-2xl font-bold text-green-400">{repo.total_variables}</p>
              </div>
              <div>
                <p className="text-slate-400">Providers</p>
                <p className="text-2xl font-bold text-orange-400">{repo.providers_count}</p>
              </div>
            </div>

            {repo.status === 'completed' && (
              <Link
                href={`/graph/${repo.id}`}
                className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition"
              >
                View Graph
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
