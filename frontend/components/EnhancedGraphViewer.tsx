'use client'

import { useCallback, useEffect, useState, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MiniMap,
  NodeTypes,
  Panel,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'
import toast from 'react-hot-toast'
import { Search, X, ZoomIn, ZoomOut, Maximize2, Filter, Eye, EyeOff } from 'lucide-react'
import ResourceNode from './graph/ResourceNode'
import VariableNode from './graph/VariableNode'
import ModuleNode from './graph/ModuleNode'
import ProviderNode from './graph/ProviderNode'
import OutputNode from './graph/OutputNode'
import GraphCommandPalette from './GraphCommandPalette'

const nodeTypes: NodeTypes = {
  resource: ResourceNode,
  variable: VariableNode,
  module: ModuleNode,
  provider: ProviderNode,
  output: OutputNode,
}

// Node type colors for dark theme
const NODE_COLORS = {
  resource: '#3b82f6',    // blue
  module: '#8b5cf6',      // purple
  variable: '#10b981',    // green
  output: '#f59e0b',      // orange
  provider: '#ef4444',    // red
  local: '#06b6d4',       // cyan
  data_source: '#ec4899', // pink
}

interface Props {
  repoId: number
}

function GraphViewerContent({ repoId }: Props) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set())
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showMiniMap, setShowMiniMap] = useState(true)
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  
  const { fitView, zoomIn, zoomOut } = useReactFlow()

  // Keyboard shortcut for command palette (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsCommandPaletteOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Handle node selection from command palette
  const handleNodeSelectFromPalette = useCallback((nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId)
    if (node) {
      setSelectedNode(node)
      // Center on the selected node
      fitView({ nodes: [node], duration: 500, padding: 0.5 })
    }
  }, [nodes, fitView])

  // Fetch graph data
  useEffect(() => {
    const fetchGraph = async () => {
      setIsLoading(true)
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/api/graphs/${repoId}/dependency-graph`
        )

        const graphData = response.data
        
        // Convert to React Flow format with better layout
        const flowNodes: Node[] = graphData.nodes.map((node: any, idx: number) => {
          const nodeType = node.type || 'default'
          
          return {
            id: node.id,
            data: {
              label: node.label,
              ...node.data,
            },
            position: calculateNodePosition(idx, graphData.nodes.length),
            type: nodeType,
            style: {
              background: NODE_COLORS[nodeType as keyof typeof NODE_COLORS] || '#64748b',
              color: '#ffffff',
              border: '2px solid #1e293b',
              borderRadius: '8px',
              padding: '10px',
              fontSize: '12px',
              fontWeight: '500',
            },
          }
        })

        const flowEdges: Edge[] = graphData.edges.map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.data?.relationshipType || '',
          type: 'smoothstep',
          animated: false,
          style: {
            stroke: '#475569',
            strokeWidth: 2,
          },
          labelStyle: {
            fill: '#94a3b8',
            fontSize: 10,
          },
        }))

        setNodes(flowNodes)
        setEdges(flowEdges)
        
        // Fit view after a short delay
        setTimeout(() => fitView({ padding: 0.2 }), 100)
      } catch (error) {
        toast.error('Failed to load graph')
        console.error(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchGraph()
  }, [repoId, setNodes, setEdges, fitView])

  // Calculate node position in a circular/grid layout
  const calculateNodePosition = (index: number, total: number) => {
    const cols = Math.ceil(Math.sqrt(total))
    const row = Math.floor(index / cols)
    const col = index % cols
    
    return {
      x: col * 300 + 100,
      y: row * 200 + 100,
    }
  }

  // Filter nodes based on search and type
  const filteredNodes = useMemo(() => {
    return nodes.filter(node => {
      const matchesSearch = searchTerm === '' || 
        node.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.data.label?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesType = filterType === 'all' || node.type === filterType
      
      return matchesSearch && matchesType
    })
  }, [nodes, searchTerm, filterType])

  // Highlight dependencies when node is selected
  useEffect(() => {
    if (!selectedNode) {
      setHighlightedNodes(new Set())
      setHighlightedEdges(new Set())
      
      // Reset all node and edge styles
      setNodes(nodes => nodes.map(node => ({
        ...node,
        style: {
          ...node.style,
          opacity: 1,
          border: '2px solid #1e293b',
        }
      })))
      
      setEdges(edges => edges.map(edge => ({
        ...edge,
        animated: false,
        style: {
          ...edge.style,
          stroke: '#475569',
          strokeWidth: 2,
          opacity: 1,
        }
      })))
      
      return
    }

    // Find connected nodes and edges
    const connectedNodeIds = new Set<string>([selectedNode.id])
    const connectedEdgeIds = new Set<string>()

    edges.forEach(edge => {
      if (edge.source === selectedNode.id) {
        connectedNodeIds.add(edge.target)
        connectedEdgeIds.add(edge.id)
      }
      if (edge.target === selectedNode.id) {
        connectedNodeIds.add(edge.source)
        connectedEdgeIds.add(edge.id)
      }
    })

    setHighlightedNodes(connectedNodeIds)
    setHighlightedEdges(connectedEdgeIds)

    // Update node styles
    setNodes(nodes => nodes.map(node => ({
      ...node,
      style: {
        ...node.style,
        opacity: connectedNodeIds.has(node.id) ? 1 : 0.3,
        border: node.id === selectedNode.id 
          ? '3px solid #fbbf24' 
          : connectedNodeIds.has(node.id)
          ? '2px solid #60a5fa'
          : '2px solid #1e293b',
      }
    })))

    // Update edge styles
    setEdges(edges => edges.map(edge => ({
      ...edge,
      animated: connectedEdgeIds.has(edge.id),
      style: {
        ...edge.style,
        stroke: connectedEdgeIds.has(edge.id) ? '#60a5fa' : '#475569',
        strokeWidth: connectedEdgeIds.has(edge.id) ? 3 : 2,
        opacity: connectedEdgeIds.has(edge.id) ? 1 : 0.3,
      }
    })))
  }, [selectedNode, edges, setNodes, setEdges])

  // Get unique node types for filter
  const nodeTypeOptions = useMemo(() => {
    const types = new Set(nodes.map(n => n.type))
    return ['all', ...Array.from(types)]
  }, [nodes])

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="inline-block animate-spin mb-4">
            <div className="w-12 h-12 border-4 border-slate-700 border-t-blue-500 rounded-full"></div>
          </div>
          <p className="text-slate-400 text-lg">Loading dependency graph...</p>
        </div>
      </div>
    )
  }

      {/* Command Palette */}
      <GraphCommandPalette
        repoId={repoId}
        nodes={nodes}
        onNodeSelect={handleNodeSelectFromPalette}
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />

  return (
    <div className={`relative bg-slate-900 ${isFullscreen ? 'fixed inset-0 z-50' : 'w-full h-full'}`}>
      <ReactFlow
        nodes={filteredNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={(event, node) => setSelectedNode(node)}
        fitView
        attributionPosition="bottom-left"
        className="bg-slate-900"
      >
        <Background color="#334155" gap={20} size={1} />
        <Controls 
          className="bg-slate-800 border border-slate-700"
          showInteractive={false}
        />
        {showMiniMap && (
          <MiniMap 
            nodeColor={(node) => NODE_COLORS[node.type as keyof typeof NODE_COLORS] || '#64748b'}
            className="bg-slate-800 border border-slate-700"
            maskColor="rgba(15, 23, 42, 0.8)"
          />
        )}

        {/* Top Control Panel */}
        <Panel position="top-left" className="flex gap-2">
          {/* Search */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-transparent text-white text-sm outline-none w-48"
            />
            {searchTerm && (
              <button onClick={() => setSearchTerm('')} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Filter */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-transparent text-white text-sm outline-none"
            >
              {nodeTypeOptions.map(type => (
                <option key={type} value={type} className="bg-slate-800">
                  {type === 'all' ? 'All Types' : type}
                </option>
              ))}
            </select>
          </div>
        </Panel>

        {/* Top Right Controls */}
        <Panel position="top-right" className="flex gap-2">
          <button
            onClick={() => setShowMiniMap(!showMiniMap)}
            className="bg-slate-800 border border-slate-700 rounded-lg p-2 text-slate-400 hover:text-white hover:bg-slate-700"
            title={showMiniMap ? "Hide minimap" : "Show minimap"}
          >
            {showMiniMap ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
          
          <button
            onClick={toggleFullscreen}
            className="bg-slate-800 border border-slate-700 rounded-lg p-2 text-slate-400 hover:text-white hover:bg-slate-700"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </Panel>

        {/* Stats Panel */}
        <Panel position="bottom-right" className="bg-slate-800 border border-slate-700 rounded-lg p-3">
          <div className="text-xs space-y-1">
            <div className="flex justify-between gap-4">
              <span className="text-slate-400">Nodes:</span>
              <span className="text-white font-mono">{filteredNodes.length}/{nodes.length}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-slate-400">Edges:</span>
              <span className="text-white font-mono">{edges.length}</span>
            </div>
            {selectedNode && (
              <div className="flex justify-between gap-4 pt-1 border-t border-slate-700">
                <span className="text-slate-400">Selected:</span>
                <span className="text-blue-400 font-mono">{highlightedNodes.size - 1}</span>
              </div>
            )}
          </div>
        </Panel>
      </ReactFlow>

      {/* Node Details Sidebar */}
      {selectedNode && (
        <div className="absolute right-0 top-0 w-96 h-full bg-slate-800 border-l border-slate-700 overflow-y-auto shadow-2xl">
          <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center z-10">
            <h3 className="text-lg font-semibold text-white">Node Details</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white p-1 hover:bg-slate-700 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 space-y-4">
            {/* Node ID */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">ID</p>
              <p className="text-white font-mono text-sm break-all bg-slate-900 p-2 rounded">
                {selectedNode.id}
              </p>
            </div>

            {/* Node Type */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Type</p>
              <span 
                className="inline-block px-3 py-1 rounded-full text-sm font-medium"
                style={{ 
                  backgroundColor: NODE_COLORS[selectedNode.type as keyof typeof NODE_COLORS] + '40',
                  color: NODE_COLORS[selectedNode.type as keyof typeof NODE_COLORS] || '#64748b'
                }}
              >
                {selectedNode.type}
              </span>
            </div>

            {/* Dependencies */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Dependencies</p>
              <div className="space-y-2">
                <div className="bg-slate-900 p-2 rounded">
                  <p className="text-xs text-slate-400">Depends on:</p>
                  <p className="text-white font-mono text-sm">
                    {edges.filter(e => e.source === selectedNode.id).length} nodes
                  </p>
                </div>
                <div className="bg-slate-900 p-2 rounded">
                  <p className="text-xs text-slate-400">Depended by:</p>
                  <p className="text-white font-mono text-sm">
                    {edges.filter(e => e.target === selectedNode.id).length} nodes
                  </p>
                </div>
              </div>
            </div>

            {/* Node Data */}
            {selectedNode.data && Object.keys(selectedNode.data).length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Properties</p>
                <div className="bg-slate-900 rounded p-3 text-xs font-mono text-slate-300 overflow-x-auto">
                  <pre className="whitespace-pre-wrap break-words">
                    {JSON.stringify(selectedNode.data, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* Connected Nodes */}
            {highlightedNodes.size > 1 && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase mb-2">
                  Connected Nodes ({highlightedNodes.size - 1})
                </p>
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {Array.from(highlightedNodes)
                    .filter(id => id !== selectedNode.id)
                    .map(nodeId => {
                      const node = nodes.find(n => n.id === nodeId)
                      return node ? (
                        <div 
                          key={nodeId}
                          className="bg-slate-900 p-2 rounded text-xs hover:bg-slate-700 cursor-pointer"
                          onClick={() => setSelectedNode(node)}
                        >
                          <p className="text-white font-mono truncate">{nodeId}</p>
                          <p className="text-slate-400 capitalize">{node.type}</p>
                        </div>
                      ) : null
                    })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      {!selectedNode && (
        <div className="absolute left-4 bottom-20 bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Legend</p>
          <div className="space-y-1">
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs text-slate-300 capitalize">{type.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function EnhancedGraphViewer(props: Props) {
  return (
    <ReactFlowProvider>
      <GraphViewerContent {...props} />
    </ReactFlowProvider>
  )
}

// Made with Bob
