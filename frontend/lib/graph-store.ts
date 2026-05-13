import { create } from 'zustand'

interface Graph {
  nodes: any[]
  edges: any[]
  statistics: {
    node_count: number
    edge_count: number
  }
}

interface GraphStore {
  currentGraph: Graph | null
  setCurrentGraph: (graph: Graph | null) => void
  selectedNode: string | null
  setSelectedNode: (nodeId: string | null) => void
  zoomLevel: number
  setZoomLevel: (zoom: number) => void
}

export const useGraphStore = create<GraphStore>((set) => ({
  currentGraph: null,
  setCurrentGraph: (graph) => set({ currentGraph: graph }),
  selectedNode: null,
  setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),
  zoomLevel: 1,
  setZoomLevel: (zoom) => set({ zoomLevel: zoom }),
}))
