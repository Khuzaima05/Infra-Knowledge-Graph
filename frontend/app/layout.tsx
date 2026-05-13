import type { Metadata } from 'next'
import './globals.css'

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
    <html lang="en">
      <body className="bg-background text-foreground">
        {children}
      </body>
    </html>
  )
}
