'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import GraphViewer from '@/components/GraphViewer'

export default function GraphPage() {
  const params = useParams()
  const repoId = params.id as string
  const [repository, setRepository] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'graph' | 'summary'>('graph')

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const [repoRes, summaryRes] = await Promise.all([
          axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/repositories/${repoId}`),
          axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/graphs/${repoId}/summary`).catch(() => ({ data: null }))
        ])

        setRepository(repoRes.data)
        setSummary(summaryRes.data)
      } catch (error) {
        toast.error('Failed to load repository data')
        console.error(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [repoId])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin mb-4">
            <div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full"></div>
          </div>
          <p className="text-slate-400">Loading graph...</p>
        </div>
      </div>
    )
  }

  if (!repository) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-slate-400">Repository not found</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="border-b border-slate-700 bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">{repository.name}</h1>
              <p className="text-slate-400 text-sm mt-1">{repository.url}</p>
            </div>
            <a href="/dashboard" className="text-blue-400 hover:text-blue-300">
              ← Back to Dashboard
            </a>
          </div>
        </div>
      </header>

      {/* Statistics */}
      <div className="border-b border-slate-700 bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Resources" value={repository.statistics.total_resources} color="blue" />
            <StatCard label="Modules" value={repository.statistics.total_modules} color="purple" />
            <StatCard label="Variables" value={repository.statistics.total_variables} color="green" />
            <StatCard label="Providers" value={repository.statistics.providers_count} color="orange" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-700 bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('graph')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'graph'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-white'
              }`}
            >
              Dependency Graph
            </button>
            {summary && (
              <button
                onClick={() => setActiveTab('summary')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'summary'
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-white'
                }`}
              >
                Architecture Summary
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {activeTab === 'graph' ? (
          <div className="h-[calc(100vh-400px)] bg-card border-b border-slate-700">
            <GraphViewer repoId={parseInt(repoId)} />
          </div>
        ) : (
          <div className="p-8">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">{summary?.title}</h2>
                <p className="text-slate-300">{summary?.architecture_description}</p>
              </div>

              {summary?.deployment_overview && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Deployment Overview</h3>
                  <p className="text-slate-300">{summary.deployment_overview}</p>
                </div>
              )}

              {summary?.key_components && summary.key_components.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Key Components</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {summary.key_components.map((component: any, idx: number) => (
                      <div key={idx} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                        <p className="font-medium text-white">{component.name}</p>
                        <p className="text-slate-400 text-sm mt-1">{component.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colorMap = {
    blue: 'text-blue-400 bg-blue-900/20',
    purple: 'text-purple-400 bg-purple-900/20',
    green: 'text-green-400 bg-green-900/20',
    orange: 'text-orange-400 bg-orange-900/20',
  }

  return (
    <div className={`rounded-lg p-4 ${colorMap[color as keyof typeof colorMap]}`}>
      <p className="text-slate-400 text-sm">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  )
}
