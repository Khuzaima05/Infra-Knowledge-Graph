'use client'

import { useCallback, useEffect, useState } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MiniMap,
  NodeTypes,
} from 'reactflow'
import 'reactflow/dist/style.css'
import axios from 'axios'
import toast from 'react-hot-toast'
import ResourceNode from './graph/ResourceNode'
import VariableNode from './graph/VariableNode'
import ModuleNode from './graph/ModuleNode'
import ProviderNode from './graph/ProviderNode'
import OutputNode from './graph/OutputNode'

const nodeTypes: NodeTypes = {
  resource: ResourceNode,
  variable: VariableNode,
  module: ModuleNode,
  provider: ProviderNode,
  output: OutputNode,
}

interface Props {
  repoId: number
}

export default function GraphViewer({ repoId }: Props) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)

  useEffect(() => {
    const fetchGraph = async () => {
      setIsLoading(true)
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/api/graphs/${repoId}/dependency-graph`
        )

        const graphData = response.data
        
        // Convert to React Flow format
        const flowNodes: Node[] = graphData.nodes.map((node: any, idx: number) => ({
          id: node.id,
          data: {
            label: node.label,
            ...node.data,
          },
          position: {
            x: (idx % 5) * 250,
            y: Math.floor(idx / 5) * 250,
          },
          type: node.type || 'default',
        }))

        const flowEdges: Edge[] = graphData.edges.map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.data?.relationshipType || '',
        }))

        setNodes(flowNodes)
        setEdges(flowEdges)
      } catch (error) {
        toast.error('Failed to load graph')
        console.error(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchGraph()
  }, [repoId, setNodes, setEdges])

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-card">
        <div className="text-center">
          <div className="inline-block animate-spin mb-4">
            <div className="w-8 h-8 border-4 border-slate-700 border-t-blue-500 rounded-full"></div>
          </div>
          <p className="text-slate-400">Loading graph...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={(event, node) => setSelectedNode(node)}
      >
        <Background color="#374151" />
        <Controls />
        <MiniMap />
      </ReactFlow>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="absolute right-0 top-0 w-80 h-full bg-card border-l border-slate-700 overflow-y-auto p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-white">Node Details</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase">ID</p>
              <p className="text-white font-mono text-sm break-all">{selectedNode.id}</p>
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase">Type</p>
              <p className="text-white capitalize">{selectedNode.type}</p>
            </div>

            {selectedNode.data && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Data</p>
                <div className="bg-slate-800 rounded p-2 text-xs font-mono text-slate-300 overflow-x-auto">
                  <pre>{JSON.stringify(selectedNode.data, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
