export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <header className="border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-white">
              Infra Knowledge Graph
            </h1>
            <a href="/dashboard" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium">
              Go to Dashboard
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-6">
            Understand Your Infrastructure
          </h2>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-8">
            Analyze Terraform repositories and automatically generate dependency graphs,
            module lineage diagrams, and searchable infrastructure intelligence.
          </p>
          <a href="/dashboard" className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold text-lg">
            Start Analyzing
          </a>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-20">
          <FeatureCard
            title="Dependency Graphs"
            description="Visualize how resources, modules, and variables interact with each other"
            icon="🔗"
          />
          <FeatureCard
            title="Module Lineage"
            description="Track module inheritance and relationships across your infrastructure"
            icon="📦"
          />
          <FeatureCard
            title="Variable Maps"
            description="Understand variable usage patterns and dependencies"
            icon="🗺️"
          />
          <FeatureCard
            title="Architecture Summaries"
            description="Get AI-powered insights about your infrastructure design"
            icon="🤖"
          />
          <FeatureCard
            title="Full-text Search"
            description="Search across all infrastructure components"
            icon="🔍"
          />
          <FeatureCard
            title="Interactive Visualization"
            description="Explore complex infrastructures with intuitive graph interactions"
            icon="📊"
          />
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="bg-card border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}
