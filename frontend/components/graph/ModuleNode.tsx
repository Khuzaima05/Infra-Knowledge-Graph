'use client'

import { Handle, Position } from 'reactflow'

export default function ModuleNode({ data }: any) {
  return (
    <div className="bg-purple-900 border-2 border-purple-500 rounded-lg p-3 min-w-max">
      <Handle type="target" position={Position.Top} />
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">📚</span>
        <p className="font-semibold text-purple-100 text-sm">{data.label}</p>
      </div>
      {data.source && (
        <p className="text-xs text-purple-300 truncate">{data.source}</p>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
