# Frontend Shell Implementation Guide

Complete guide for implementing the modern dark UI shell with Next.js 15 and shadcn/ui.

## Overview

This guide provides the complete implementation for a modern, dark-themed developer tool UI with:
- Collapsible sidebar navigation
- Responsive layout
- Top navigation bar
- Dashboard cards
- Fullscreen graph mode
- Four main pages

## Architecture

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with sidebar
│   ├── page.tsx                # Redirect to dashboard
│   ├── dashboard/
│   │   └── page.tsx            # Main dashboard
│   ├── repositories/
│   │   ├── page.tsx            # Repository list
│   │   └── [id]/
│   │       └── page.tsx        # Repository details
│   ├── graph/
│   │   └── [id]/
│   │       └── page.tsx        # Graph visualization
│   └── summary/
│       └── [id]/
│           └── page.tsx        # Architecture summary
├── components/
│   ├── ui/
│   │   ├── sidebar.tsx         # ✅ Created
│   │   ├── card.tsx            # Dashboard cards
│   │   ├── button.tsx          # Button component
│   │   └── badge.tsx           # Status badges
│   ├── layout/
│   │   ├── app-sidebar.tsx     # Main sidebar with nav
│   │   ├── top-nav.tsx         # Top navigation bar
│   │   └── page-header.tsx     # Page header component
│   └── dashboard/
│       ├── stats-card.tsx      # Statistics card
│       ├── repo-card.tsx       # Repository card
│       └── activity-feed.tsx   # Recent activity
└── lib/
    ├── utils.ts                # ✅ Updated with cn()
    └── api.ts                  # API client
```

## Components to Create

### 1. Card Component (`components/ui/card.tsx`)

```typescript
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border border-slate-800 bg-slate-900/50 text-slate-100 shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-slate-400", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

### 2. App Sidebar (`components/layout/app-sidebar.tsx`)

```typescript
"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Database,
  Network,
  FileText,
  Settings,
  GitBranch
} from "lucide-react"
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarNav,
  SidebarNavItem,
  SidebarSection,
  SidebarToggle,
} from "@/components/ui/sidebar"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Repositories", href: "/repositories", icon: Database },
  { name: "Graph View", href: "/graph", icon: Network },
  { name: "Summaries", href: "/summary", icon: FileText },
]

const tools = [
  { name: "Analyze Repo", href: "/analyze", icon: GitBranch },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarToggle />
      
      <SidebarHeader>
        <div className="flex items-center gap-2">
          <Network className="h-6 w-6 text-sky-400" />
          <span className="font-bold text-lg">Infra Graph</span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarSection title="Main">
          <SidebarNav>
            {navigation.map((item) => (
              <Link key={item.name} href={item.href} passHref legacyBehavior>
                <SidebarNavItem
                  icon={<item.icon className="h-5 w-5" />}
                  active={pathname === item.href}
                >
                  {item.name}
                </SidebarNavItem>
              </Link>
            ))}
          </SidebarNav>
        </SidebarSection>

        <SidebarSection title="Tools">
          <SidebarNav>
            {tools.map((item) => (
              <Link key={item.name} href={item.href} passHref legacyBehavior>
                <SidebarNavItem
                  icon={<item.icon className="h-5 w-5" />}
                  active={pathname === item.href}
                >
                  {item.name}
                </SidebarNavItem>
              </Link>
            ))}
          </SidebarNav>
        </SidebarSection>
      </SidebarContent>

      <SidebarFooter>
        <div className="text-xs text-slate-500">
          v1.0.0
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
```

### 3. Top Navigation (`components/layout/top-nav.tsx`)

```typescript
"use client"

import { Bell, Search, User } from "lucide-react"

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/95 backdrop-blur supports-[backdrop-filter]:bg-slate-950/60">
      <div className="flex h-16 items-center gap-4 px-6">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search repositories..."
              className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2 pl-10 pr-4 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button className="rounded-lg p-2 text-slate-400 hover:bg-slate-900 hover:text-slate-100">
            <Bell className="h-5 w-5" />
          </button>
          <button className="rounded-lg p-2 text-slate-400 hover:bg-slate-900 hover:text-slate-100">
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
```

### 4. Root Layout (`app/layout.tsx`)

```typescript
import type { Metadata } from 'next'
import './globals.css'
import { SidebarProvider } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/layout/app-sidebar'
import { TopNav } from '@/components/layout/top-nav'

export const metadata: Metadata = {
  title: 'Infra Knowledge Graph',
  description: 'Analyze Terraform repositories and visualize infrastructure dependencies',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased">
        <SidebarProvider>
          <div className="flex h-screen overflow-hidden">
            <AppSidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
              <TopNav />
              <main className="flex-1 overflow-y-auto">
                {children}
              </main>
            </div>
          </div>
        </SidebarProvider>
      </body>
    </html>
  )
}
```

### 5. Dashboard Page (`app/dashboard/page.tsx`)

```typescript
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, Network, GitBranch, Activity } from "lucide-react"

export default function DashboardPage() {
  const stats = [
    {
      title: "Total Repositories",
      value: "12",
      change: "+2 this week",
      icon: Database,
      color: "text-sky-400"
    },
    {
      title: "Total Resources",
      value: "1,234",
      change: "+156 this week",
      icon: Network,
      color: "text-emerald-400"
    },
    {
      title: "Dependencies",
      value: "2,456",
      change: "+89 this week",
      icon: GitBranch,
      color: "text-violet-400"
    },
    {
      title: "Active Analyses",
      value: "3",
      change: "2 completed today",
      icon: Activity,
      color: "text-amber-400"
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-slate-400">
          Overview of your infrastructure analysis
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-slate-400">{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Repositories */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Repositories</CardTitle>
          <CardDescription>
            Latest analyzed Terraform repositories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Repository list items */}
            <p className="text-sm text-slate-400">
              No repositories analyzed yet. Start by analyzing a repository.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

## Styling Updates

### Update `app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-slate-800;
  }
  
  body {
    @apply bg-slate-950 text-slate-100;
  }
}

@layer utilities {
  .scrollbar-thin::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    @apply bg-slate-900;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    @apply bg-slate-700 rounded-full;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    @apply bg-slate-600;
  }
}
```

### Update `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
}
export default config
```

## Implementation Steps

1. **Install Dependencies** (if needed)
```bash
cd frontend
npm install clsx tailwind-merge class-variance-authority
```

2. **Create UI Components**
   - ✅ `components/ui/sidebar.tsx` (Already created)
   - Create `components/ui/card.tsx`
   - Create `components/ui/button.tsx`
   - Create `components/ui/badge.tsx`

3. **Create Layout Components**
   - Create `components/layout/app-sidebar.tsx`
   - Create `components/layout/top-nav.tsx`
   - Create `components/layout/page-header.tsx`

4. **Update Root Layout**
   - Update `app/layout.tsx` with sidebar and top nav
   - Update `app/globals.css` with custom styles

5. **Create Pages**
   - Update `app/dashboard/page.tsx`
   - Create `app/repositories/[id]/page.tsx`
   - Update `app/graph/[id]/page.tsx`
   - Create `app/summary/[id]/page.tsx`

## Features

### Collapsible Sidebar
- ✅ Implemented with `SidebarProvider` context
- Toggle button with smooth animation
- Icons remain visible when collapsed
- Responsive width (64px collapsed, 256px expanded)

### Dark Modern UI
- Slate color palette (950, 900, 800 for backgrounds)
- Sky blue accents for interactive elements
- Subtle borders and shadows
- Smooth transitions

### Responsive Layout
- Flexbox-based layout
- Mobile-friendly sidebar (can be hidden)
- Responsive grid for dashboard cards
- Overflow handling for content areas

### Top Navigation
- Sticky header with backdrop blur
- Global search bar
- Notification and user menu icons
- Consistent height (64px)

### Dashboard Cards
- Reusable Card component
- Statistics cards with icons
- Color-coded metrics
- Hover effects

### Fullscreen Graph Mode
- Implement in `app/graph/[id]/page.tsx`
- Toggle button for fullscreen
- Escape key to exit
- Preserved graph state

## Color Palette

```
Background: slate-950 (#020617)
Card: slate-900 (#0f172a)
Border: slate-800 (#1e293b)
Text: slate-100 (#f1f5f9)
Muted: slate-400 (#94a3b8)
Primary: sky-500 (#0ea5e9)
Success: emerald-500 (#10b981)
Warning: amber-500 (#f59e0b)
Danger: red-500 (#ef4444)
```

## Next Steps

1. Implement remaining UI components
2. Connect to dashboard API endpoints
3. Add loading states and error handling
4. Implement graph visualization page
5. Add repository details page
6. Create architecture summary page
7. Add animations and transitions
8. Implement search functionality
9. Add user preferences/settings
10. Test responsive behavior

## Resources

- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Lucide Icons](https://lucide.dev/)
- [React Flow](https://reactflow.dev/) (for graph visualization)