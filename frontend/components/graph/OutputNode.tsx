'use client'

import { Handle, Position } from 'reactflow'

export default function OutputNode({ data }: any) {
  return (
    <div className="bg-cyan-900 border-2 border-cyan-500 rounded-lg p-3 min-w-max">
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">📤</span>
        <p className="font-semibold text-cyan-100 text-sm">{data.label}</p>
      </div>
      {data.description && (
        <p className="text-xs text-cyan-300 max-w-32">{data.description}</p>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
