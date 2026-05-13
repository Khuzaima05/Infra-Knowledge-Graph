'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'

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

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchRepositories()
  }, [])

  const fetchRepositories = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/repositories`
      )
      setRepositories(response.data)
    } catch (err) {
      const message = 'Failed to load repositories'
      setError(message)
      toast.error(message)
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin mb-4">
            <div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full"></div>
          </div>
          <p className="text-slate-400">Loading repositories...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Repositories</h1>
              <p className="text-slate-400 mt-1">All analyzed Terraform repositories</p>
            </div>
            <Link href="/dashboard" className="text-blue-400 hover:text-blue-300 font-medium">
              Add New →
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {repositories.length === 0 ? (
          <div className="text-center py-16 bg-card border border-slate-700 rounded-lg">
            <p className="text-slate-400 text-lg mb-4">No repositories analyzed yet</p>
            <Link
              href="/dashboard"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
            >
              Analyze a Repository
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Name</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Status</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Resources</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Modules</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Variables</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Providers</th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-slate-300">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {repositories.map((repo) => (
                    <tr key={repo.id} className="border-b border-slate-700 hover:bg-slate-900/50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-white">{repo.name}</p>
                          <p className="text-xs text-slate-500 truncate">{repo.url}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            repo.status === 'completed'
                              ? 'bg-green-900 text-green-200'
                              : repo.status === 'failed'
                              ? 'bg-red-900 text-red-200'
                              : 'bg-yellow-900 text-yellow-200'
                          }`}
                        >
                          {repo.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-white font-mono">{repo.total_resources}</td>
                      <td className="px-6 py-4 text-white font-mono">{repo.total_modules}</td>
                      <td className="px-6 py-4 text-white font-mono">{repo.total_variables}</td>
                      <td className="px-6 py-4 text-white font-mono">{repo.providers_count}</td>
                      <td className="px-6 py-4 text-right">
                        {repo.status === 'completed' && (
                          <Link
                            href={`/graph/${repo.id}`}
                            className="text-blue-400 hover:text-blue-300 font-medium text-sm"
                          >
                            View Graph →
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
