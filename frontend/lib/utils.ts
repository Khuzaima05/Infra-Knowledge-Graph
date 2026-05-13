// Utility functions for the frontend
import axios from 'axios'
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatBytes = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
}

export const formatDate = (date: string | Date): string => {
  const d = new Date(date)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
}

export const truncate = (str: string, length: number): string => {
  return str.length > length ? str.substring(0, length) + '...' : str
}

export const getNodeColor = (nodeType: string): string => {
  const colors: { [key: string]: string } = {
    resource: '#3B82F6',
    variable: '#10B981',
    module: '#8B5CF6',
    provider: '#F59E0B',
    output: '#06B6D4',
    local: '#EC4899',
    data: '#14B8A6',
  }
  return colors[nodeType] || '#6B7280'
}

export const getNodeShape = (nodeType: string): string => {
  const shapes: { [key: string]: string } = {
    resource: 'square',
    variable: 'circle',
    module: 'diamond',
    provider: 'hexagon',
    output: 'triangle',
    local: 'ellipse',
  }
  return shapes[nodeType] || 'default'
}
