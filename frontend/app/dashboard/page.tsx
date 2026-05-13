'use client'

import { useState } from 'react'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import RepositoryForm from '@/components/RepositoryForm'
import RepositoryList from '@/components/RepositoryList'

export default function DashboardPage() {
  const [repositories, setRepositories] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchRepositories = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/repositories`
      )
      setRepositories(response.data)
    } catch (error) {
      toast.error('Failed to load repositories')
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRepositoryAdded = (newRepo: any) => {
    fetchRepositories()
    toast.success('Repository analysis started!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <Toaster position="top-right" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            Infrastructure Knowledge Graph
          </h1>
          <p className="text-slate-400">
            Analyze Terraform repositories and visualize infrastructure dependencies
          </p>
        </div>

        {/* Repository Form */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="lg:col-span-1">
            <RepositoryForm onRepositoryAdded={handleRepositoryAdded} />
          </div>
        </div>

        {/* Repository List */}
        <RepositoryList 
          repositories={repositories}
          isLoading={isLoading}
          onLoad={fetchRepositories}
        />
      </main>
    </div>
  )
}
