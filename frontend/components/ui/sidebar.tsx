"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface SidebarContextValue {
  isCollapsed: boolean
  toggleCollapse: () => void
}

const SidebarContext = React.createContext<SidebarContextValue | undefined>(undefined)

export function useSidebar() {
  const context = React.useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

interface SidebarProviderProps {
  children: React.ReactNode
  defaultCollapsed?: boolean
}

export function SidebarProvider({ children, defaultCollapsed = false }: SidebarProviderProps) {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed)

  const toggleCollapse = React.useCallback(() => {
    setIsCollapsed((prev) => !prev)
  }, [])

  return (
    <SidebarContext.Provider value={{ isCollapsed, toggleCollapse }}>
      {children}
    </SidebarContext.Provider>
  )
}

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function Sidebar({ children, className, ...props }: SidebarProps) {
  const { isCollapsed } = useSidebar()

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-800 bg-slate-950 transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
        className
      )}
      {...props}
    >
      {children}
    </aside>
  )
}

interface SidebarHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarHeader({ children, className, ...props }: SidebarHeaderProps) {
  return (
    <div
      className={cn("flex h-16 items-center border-b border-slate-800 px-4", className)}
      {...props}
    >
      {children}
    </div>
  )
}

interface SidebarContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarContent({ children, className, ...props }: SidebarContentProps) {
  return (
    <div className={cn("flex-1 overflow-y-auto py-4", className)} {...props}>
      {children}
    </div>
  )
}

interface SidebarFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarFooter({ children, className, ...props }: SidebarFooterProps) {
  return (
    <div
      className={cn("border-t border-slate-800 p-4", className)}
      {...props}
    >
      {children}
    </div>
  )
}

interface SidebarToggleProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function SidebarToggle({ className, ...props }: SidebarToggleProps) {
  const { isCollapsed, toggleCollapse } = useSidebar()

  return (
    <button
      onClick={toggleCollapse}
      className={cn(
        "absolute -right-3 top-20 z-10 flex h-6 w-6 items-center justify-center rounded-full border border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-900 hover:text-slate-100 transition-colors",
        className
      )}
      {...props}
    >
      {isCollapsed ? (
        <ChevronRight className="h-4 w-4" />
      ) : (
        <ChevronLeft className="h-4 w-4" />
      )}
    </button>
  )
}

interface SidebarNavProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode
}

export function SidebarNav({ children, className, ...props }: SidebarNavProps) {
  return (
    <nav className={cn("space-y-1 px-2", className)} {...props}>
      {children}
    </nav>
  )
}

interface SidebarNavItemProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  icon?: React.ReactNode
  active?: boolean
  children: React.ReactNode
}

export function SidebarNavItem({
  icon,
  active,
  children,
  className,
  ...props
}: SidebarNavItemProps) {
  const { isCollapsed } = useSidebar()

  return (
    <a
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-sky-500/10 text-sky-400"
          : "text-slate-400 hover:bg-slate-900 hover:text-slate-100",
        isCollapsed && "justify-center",
        className
      )}
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {!isCollapsed && <span>{children}</span>}
    </a>
  )
}

interface SidebarSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  children: React.ReactNode
}

export function SidebarSection({ title, children, className, ...props }: SidebarSectionProps) {
  const { isCollapsed } = useSidebar()

  return (
    <div className={cn("space-y-2", className)} {...props}>
      {title && !isCollapsed && (
        <h3 className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}

// Made with Bob
