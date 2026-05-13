'use client'

import { Handle, Position } from 'reactflow'

export default function ResourceNode({ data }: any) {
  return (
    <div className="bg-blue-900 border-2 border-blue-500 rounded-lg p-3 min-w-max">
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">📦</span>
        <p className="font-semibold text-blue-100 text-sm">{data.label}</p>
      </div>
      {data.resourceType && (
        <p className="text-xs text-blue-300">{data.resourceType}</p>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
