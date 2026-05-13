'use client'

import { Handle, Position } from 'reactflow'

export default function ProviderNode({ data }: any) {
  return (
    <div className="bg-orange-900 border-2 border-orange-500 rounded-lg p-3 min-w-max">
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">☁️</span>
        <p className="font-semibold text-orange-100 text-sm">{data.label}</p>
      </div>
      {data.version && (
        <p className="text-xs text-orange-300">v{data.version}</p>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
