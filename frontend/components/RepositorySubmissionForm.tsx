"use client"

import { useState } from 'react'
import { GitBranch, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
import { apiClient, type AnalyzeResponse } from '@/lib/api-client'

interface RepositorySubmissionFormProps {
  onSuccess?: (response: AnalyzeResponse) => void
}

export function RepositorySubmissionForm({ onSuccess }: RepositorySubmissionFormProps) {
  const [url, setUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [forceRefresh, setForceRefresh] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<AnalyzeResponse | null>(null)

  // GitHub URL validation
  const validateGitHubUrl = (url: string): boolean => {
    const githubPattern = /^https:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/
    return githubPattern.test(url.trim())
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    // Validate URL
    if (!url.trim()) {
      setError('Please enter a GitHub repository URL')
      return
    }

    if (!validateGitHubUrl(url)) {
      setError('Invalid GitHub URL format. Expected: https://github.com/owner/repo')
      return
    }

    setIsLoading(true)

    try {
      const response = await apiClient.analyzeRepository({
        url: url.trim(),
        branch: branch.trim() || 'main',
        force_refresh: forceRefresh,
        async_mode: true,
      })

      setSuccess(response)
      setUrl('')
      setBranch('main')
      setForceRefresh(false)

      if (onSuccess) {
        onSuccess(response)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="repo-url" className="block text-sm font-medium text-slate-200 mb-2">
            GitHub Repository URL
          </label>
          <input
            id="repo-url"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repository"
            disabled={isLoading}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <p className="mt-2 text-xs text-slate-400">
            Enter the full GitHub repository URL (e.g., https://github.com/terraform-aws-modules/terraform-aws-vpc)
          </p>
        </div>

        {/* Branch Input */}
        <div>
          <label htmlFor="branch" className="block text-sm font-medium text-slate-200 mb-2">
            Branch
          </label>
          <input
            id="branch"
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
            disabled={isLoading}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Force Refresh Checkbox */}
        <div className="flex items-center gap-2">
          <input
            id="force-refresh"
            type="checkbox"
            checked={forceRefresh}
            onChange={(e) => setForceRefresh(e.target.checked)}
            disabled={isLoading}
            className="h-4 w-4 rounded border-slate-700 bg-slate-900 text-sky-500 focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <label htmlFor="force-refresh" className="text-sm text-slate-300">
            Force refresh (re-clone if already exists)
          </label>
        </div>

        {/* Error Message */}
        {error && (
          <div className="flex items-start gap-3 rounded-lg border border-red-500/20 bg-red-500/10 p-4">
            <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-400">Error</p>
              <p className="mt-1 text-sm text-red-300">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="flex items-start gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-4">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-emerald-400">Analysis Started</p>
              <p className="mt-1 text-sm text-emerald-300">{success.message}</p>
              <p className="mt-2 text-xs text-emerald-400">
                Repository ID: {success.repository_id} • Status: {success.status}
                {success.estimated_time_seconds && (
                  <> • Estimated time: {success.estimated_time_seconds}s</>
                )}
              </p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-sky-500 px-6 py-3 text-sm font-medium text-white hover:bg-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing Repository...</span>
            </>
          ) : (
            <>
              <GitBranch className="h-4 w-4" />
              <span>Analyze Repository</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}

// Made with Bob
