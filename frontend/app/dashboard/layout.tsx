import { ReactNode } from 'react'

export default function DashboardLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <div className="flex h-screen bg-background">
      <aside className="w-64 border-r border-slate-700 bg-card hidden md:flex flex-col">
        <nav className="flex-1 px-4 py-6 space-y-2">
          <a href="/" className="block px-4 py-2 rounded-lg hover:bg-slate-700 text-primary font-semibold">
            Home
          </a>
          <a href="/repositories" className="block px-4 py-2 rounded-lg hover:bg-slate-700">
            Repositories
          </a>
          <a href="/graph" className="block px-4 py-2 rounded-lg hover:bg-slate-700">
            Graph
          </a>
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
