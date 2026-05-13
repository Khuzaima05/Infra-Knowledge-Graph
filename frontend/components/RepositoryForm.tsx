'use client'

import { FormEvent, useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface Props {
  onRepositoryAdded: (repo: any) => void
}

export default function RepositoryForm({ onRepositoryAdded }: Props) {
  const [url, setUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!url.trim()) {
      toast.error('Please enter a repository URL')
      return
    }

    setIsLoading(true)
    const toastId = toast.loading('Analyzing repository...')

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analysis`,
        {
          url: url.trim(),
          branch,
        }
      )

      toast.success('Repository analyzed successfully!', { id: toastId })
      onRepositoryAdded(response.data)
      setUrl('')
      setBranch('main')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to analyze repository'
      toast.error(message, { id: toastId })
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-card border border-slate-700 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Analyze Repository</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            GitHub Repository URL
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repository"
            className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            disabled={isLoading}
          />
          <p className="text-xs text-slate-500 mt-1">Enter the full HTTPS GitHub URL</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Branch
          </label>
          <input
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
            className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold py-2 rounded-lg transition"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      <div className="mt-6 p-4 bg-slate-800 rounded-lg">
        <p className="text-xs text-slate-400">
          <strong>Tip:</strong> Try analyzing a sample Terraform repository. The analyzer will clone, parse, and generate a dependency graph.
        </p>
      </div>
    </div>
  )
}
