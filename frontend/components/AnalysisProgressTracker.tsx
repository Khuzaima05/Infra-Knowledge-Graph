"use client"

import { useEffect, useState } from 'react'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { apiClient, type AnalysisStatus } from '@/lib/api-client'

interface AnalysisProgressTrackerProps {
  repositoryId: number
  onComplete?: (status: AnalysisStatus) => void
  onError?: (error: string) => void
}

export function AnalysisProgressTracker({
  repositoryId,
  onComplete,
  onError,
}: AnalysisProgressTrackerProps) {
  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [isPolling, setIsPolling] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null

    const fetchStatus = async () => {
      try {
        const data = await apiClient.getAnalysisStatus(repositoryId)
        setStatus(data)

        // Stop polling if analysis is complete or failed
        if (data.status === 'completed' || data.status === 'failed') {
          setIsPolling(false)
          if (intervalId) {
            clearInterval(intervalId)
          }

          if (data.status === 'completed' && onComplete) {
            onComplete(data)
          } else if (data.status === 'failed' && onError) {
            onError(data.error_message || 'Analysis failed')
          }
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch status'
        setError(errorMessage)
        setIsPolling(false)
        if (intervalId) {
          clearInterval(intervalId)
        }
        if (onError) {
          onError(errorMessage)
        }
      }
    }

    // Initial fetch
    fetchStatus()

    // Poll every 3 seconds if still analyzing
    if (isPolling) {
      intervalId = setInterval(fetchStatus, 3000)
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [repositoryId, isPolling, onComplete, onError])

  if (error) {
    return (
      <div className="flex items-start gap-3 rounded-lg border border-red-500/20 bg-red-500/10 p-4">
        <XCircle className="h-5 w-5 flex-shrink-0 text-red-400 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-medium text-red-400">Error</p>
          <p className="mt-1 text-sm text-red-300">{error}</p>
        </div>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-900/50 p-4">
        <Loader2 className="h-5 w-5 animate-spin text-sky-400" />
        <p className="text-sm text-slate-300">Loading status...</p>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-emerald-400" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-400" />
      case 'analyzing':
        return <Loader2 className="h-5 w-5 animate-spin text-sky-400" />
      case 'pending':
        return <Clock className="h-5 w-5 text-amber-400" />
      default:
        return <Clock className="h-5 w-5 text-slate-400" />
    }
  }

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'border-emerald-500/20 bg-emerald-500/10'
      case 'failed':
        return 'border-red-500/20 bg-red-500/10'
      case 'analyzing':
        return 'border-sky-500/20 bg-sky-500/10'
      case 'pending':
        return 'border-amber-500/20 bg-amber-500/10'
      default:
        return 'border-slate-700 bg-slate-900/50'
    }
  }

  const getStatusText = () => {
    switch (status.status) {
      case 'completed':
        return 'Analysis Completed'
      case 'failed':
        return 'Analysis Failed'
      case 'analyzing':
        return 'Analyzing Repository...'
      case 'pending':
        return 'Analysis Pending'
      default:
        return 'Unknown Status'
    }
  }

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
      <div className="flex items-start gap-3">
        {getStatusIcon()}
        <div className="flex-1 space-y-2">
          <div>
            <p className="text-sm font-medium text-slate-100">{getStatusText()}</p>
            <p className="text-sm text-slate-400">{status.name}</p>
          </div>

          {status.status === 'analyzing' && (
            <div className="space-y-1">
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
                <div className="h-full w-2/3 animate-pulse rounded-full bg-sky-500" />
              </div>
              <p className="text-xs text-slate-500">
                Parsing Terraform files and building dependency graph...
              </p>
            </div>
          )}

          {status.status === 'completed' && (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-slate-500">Resources:</span>{' '}
                <span className="font-medium text-slate-300">
                  {status.statistics?.total_resources || 0}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Modules:</span>{' '}
                <span className="font-medium text-slate-300">
                  {status.statistics?.total_modules || 0}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Variables:</span>{' '}
                <span className="font-medium text-slate-300">
                  {status.statistics?.total_variables || 0}
                </span>
              </div>
              <div>
                <span className="text-slate-500">Providers:</span>{' '}
                <span className="font-medium text-slate-300">
                  {status.statistics?.providers_count || 0}
                </span>
              </div>
            </div>
          )}

          {status.status === 'failed' && status.error_message && (
            <p className="text-sm text-red-300">{status.error_message}</p>
          )}

          {status.analyzed_at && (
            <p className="text-xs text-slate-500">
              Analyzed: {new Date(status.analyzed_at).toLocaleString()}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// Made with Bob
