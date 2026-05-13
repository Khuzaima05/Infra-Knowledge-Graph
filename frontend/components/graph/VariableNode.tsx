'use client'

import { Handle, Position } from 'reactflow'

export default function VariableNode({ data }: any) {
  return (
    <div className="bg-green-900 border-2 border-green-500 rounded-lg p-3 min-w-max">
      <Handle type="source" position={Position.Top} />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">🔤</span>
        <p className="font-semibold text-green-100 text-sm">{data.label}</p>
      </div>
      {data.varType && (
        <p className="text-xs text-green-300">{data.varType}</p>
      )}
      <Handle type="target" position={Position.Bottom} />
    </div>
  )
}
