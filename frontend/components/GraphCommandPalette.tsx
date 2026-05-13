'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Search, Command, ArrowRight, X } from 'lucide-react'
import { Node } from 'reactflow'

interface SearchResult {
  node_id: string
  label: string
  type: string
  data: Record<string, any>
  score: number
}

interface Props {
  repoId: number
  nodes: Node[]
  onNodeSelect: (nodeId: string) => void
  isOpen: boolean
  onClose: () => void
}

const NODE_TYPE_COLORS: Record<string, string> = {
  resource: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  module: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  variable: 'bg-green-500/20 text-green-400 border-green-500/30',
  output: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  provider: 'bg-red-500/20 text-red-400 border-red-500/30',
}

export default function GraphCommandPalette({
  repoId: _repoId,
  nodes,
  onNodeSelect,
  isOpen,
  onClose
}: Props) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
      setQuery('')
      setResults([])
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Local search (client-side)
  const searchLocal = useCallback((searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    const queryLower = searchQuery.toLowerCase()
    const matches: SearchResult[] = []

    nodes.forEach(node => {
      let score = 0
      const nodeId = node.id.toLowerCase()
      const nodeLabel = (node.data.label || '').toLowerCase()

      // Exact match in ID
      if (queryLower === nodeId) {
        score = 100
      }
      // Starts with query in ID
      else if (nodeId.startsWith(queryLower)) {
        score = 90
      }
      // Contains query in ID
      else if (nodeId.includes(queryLower)) {
        score = 70
      }
      // Exact match in label
      else if (queryLower === nodeLabel) {
        score = 80
      }
      // Starts with query in label
      else if (nodeLabel.startsWith(queryLower)) {
        score = 60
      }
      // Contains query in label
      else if (nodeLabel.includes(queryLower)) {
        score = 50
      }
      // Search in data fields
      else {
        const dataStr = JSON.stringify(node.data).toLowerCase()
        if (dataStr.includes(queryLower)) {
          score = 30
        }
      }

      if (score > 0) {
        matches.push({
          node_id: node.id,
          label: node.data.label || node.id,
          type: node.type || 'default',
          data: node.data,
          score
        })
      }
    })

    // Sort by score
    matches.sort((a, b) => b.score - a.score)

    setResults(matches.slice(0, 20))
    setSelectedIndex(0)
  }, [nodes])

  // Handle search input
  useEffect(() => {
    const debounce = setTimeout(() => {
      searchLocal(query)
    }, 150)

    return () => clearTimeout(debounce)
  }, [query, searchLocal])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev < results.length - 1 ? prev + 1 : prev
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => prev > 0 ? prev - 1 : 0)
          break
        case 'Enter':
          e.preventDefault()
          if (results[selectedIndex]) {
            handleSelect(results[selectedIndex].node_id)
          }
          break
        case 'Escape':
          e.preventDefault()
          onClose()
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, results, selectedIndex, onClose])

  // Scroll selected item into view
  useEffect(() => {
    if (resultsRef.current) {
      const selectedElement = resultsRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }
  }, [selectedIndex])

  const handleSelect = (nodeId: string) => {
    onNodeSelect(nodeId)
    onClose()
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Command Palette */}
      <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl z-50">
        <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-2xl overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-slate-700">
            <Search className="w-5 h-5 text-slate-400" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Search nodes by name, type, or ID..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent text-white text-base outline-none placeholder-slate-500"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <div className="flex items-center gap-1 text-xs text-slate-500">
              <Command className="w-3 h-3" />
              <span>K</span>
            </div>
          </div>

          {/* Results */}
          <div 
            ref={resultsRef}
            className="max-h-96 overflow-y-auto"
          >
            {results.length === 0 && query && (
              <div className="px-4 py-8 text-center text-slate-500">
                No nodes found matching "{query}"
              </div>
            )}
            
            {results.length === 0 && !query && (
              <div className="px-4 py-8 text-center text-slate-500">
                <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Start typing to search nodes...</p>
                <p className="text-xs mt-2">
                  Use ↑↓ to navigate, Enter to select, Esc to close
                </p>
              </div>
            )}

            {results.map((result, index) => (
              <button
                key={result.node_id}
                onClick={() => handleSelect(result.node_id)}
                className={`
                  w-full px-4 py-3 flex items-center gap-3 text-left
                  transition-colors
                  ${index === selectedIndex 
                    ? 'bg-slate-700' 
                    : 'hover:bg-slate-750'
                  }
                  ${index !== results.length - 1 ? 'border-b border-slate-700/50' : ''}
                `}
              >
                {/* Node Type Badge */}
                <div className={`
                  px-2 py-1 rounded text-xs font-medium border
                  ${NODE_TYPE_COLORS[result.type] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'}
                `}>
                  {result.type}
                </div>

                {/* Node Info */}
                <div className="flex-1 min-w-0">
                  <div className="text-white font-medium truncate">
                    {result.label}
                  </div>
                  <div className="text-xs text-slate-400 truncate font-mono">
                    {result.node_id}
                  </div>
                </div>

                {/* Score Badge */}
                <div className="text-xs text-slate-500">
                  {result.score}%
                </div>

                {/* Arrow */}
                {index === selectedIndex && (
                  <ArrowRight className="w-4 h-4 text-slate-400" />
                )}
              </button>
            ))}
          </div>

          {/* Footer */}
          {results.length > 0 && (
            <div className="px-4 py-2 border-t border-slate-700 flex items-center justify-between text-xs text-slate-500">
              <div>
                {results.length} result{results.length !== 1 ? 's' : ''}
              </div>
              <div className="flex items-center gap-4">
                <span>↑↓ Navigate</span>
                <span>↵ Select</span>
                <span>Esc Close</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

// Made with Bob
