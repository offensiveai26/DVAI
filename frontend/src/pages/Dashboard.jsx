import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { fetchCategories, fetchProgress } from '../api'

const DIFF_MAP = { 1: 'Easy', 2: 'Medium', 3: 'Hard' }

export default function Dashboard() {
  const [categories, setCategories] = useState([])
  const [progress, setProgress] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => {})
    fetchProgress().then(setProgress).catch(() => {})
    fetch('/health').then(r => r.json()).then(setHealth).catch(() => {})
  }, [])

  const completed = progress?.completed || 0
  const total = progress?.total || 0
  const pct = total ? Math.round((completed / total) * 100) : 0

  return (
    <div>
      {/* ── Hero ── */}
      <div className="text-center mb-16 pt-8">
        <div className="inline-block mb-6 animate-float">
          <div className="w-24 h-24 mx-auto rounded-2xl bg-accent/5 border border-accent/20 flex items-center justify-center glow-accent overflow-hidden">
            <img src="/logo.svg" alt="DVAI" className="w-20 h-20" />
          </div>
        </div>
        <h1 className="text-5xl font-black tracking-tight mb-4">
          <span className="text-gradient">Damn Vulnerable AI</span>
        </h1>
        <p className="text-muted text-lg max-w-xl mx-auto leading-relaxed">
          Master AI security by exploiting real vulnerabilities.
          <br />
          <span className="text-white/60">37 challenges. 12 categories. Zero cloud dependencies.</span>
        </p>

        {/* Quick stats */}
        <div className="flex items-center justify-center gap-8 mt-8">
          <Stat value="37" label="Challenges" />
          <div className="w-px h-8 bg-border" />
          <Stat value="12" label="Categories" />
          <div className="w-px h-8 bg-border" />
          <Stat value="3" label="Difficulty Levels" />
          <div className="w-px h-8 bg-border" />
          <Stat value="100%" label="Offline" />
        </div>
      </div>

      {/* ── Progress Card ── */}
      <div className="card-gradient p-6 mb-10">
        {/* Ollama Status Banner */}
        {health && (
          <div className={`mb-4 px-4 py-2.5 rounded-lg text-xs flex items-center gap-2 ${
            health.ollama?.includes('connected') && !health.ollama?.includes('not')
              ? 'bg-accent/5 border border-accent/20 text-accent'
              : 'bg-warning/5 border border-warning/20 text-warning'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              health.ollama?.includes('connected') && !health.ollama?.includes('not') ? 'bg-accent' : 'bg-warning animate-pulse'
            }`} />
            {health.ollama?.includes('connected') && !health.ollama?.includes('not')
              ? 'Ollama connected - all challenges available'
              : 'Ollama not detected - running in simulation mode (LLM challenges use simulated responses)'}
          </div>
        )}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
              <span className="text-sm">📊</span>
            </div>
            <div>
              <h3 className="text-sm font-semibold">Your Progress</h3>
              <p className="text-xs text-muted">Keep hacking!</p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-2xl font-bold text-accent">{completed}</span>
            <span className="text-muted text-sm">/{total}</span>
          </div>
        </div>
        <div className="w-full bg-border rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${
              pct > 0 ? 'progress-shimmer' : 'bg-border-bright'
            }`}
            style={{ width: `${Math.max(pct, 2)}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-muted">
          <span>{pct}% complete</span>
          <span>{total - completed} remaining</span>
        </div>
      </div>

      {/* ── Category Grid ── */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-muted uppercase tracking-widest mb-4">
          Challenge Categories
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {categories.map((cat, i) => (
          <Link
            key={cat.id}
            to={`/category/${cat.id}`}
            className="category-card card-gradient p-5 group cursor-pointer"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            {/* Icon */}
            <div className="w-12 h-12 rounded-xl bg-accent/5 border border-border flex items-center justify-center mb-4 group-hover:border-accent/30 group-hover:bg-accent/10 transition-all">
              <span className="text-2xl">{cat.icon}</span>
            </div>

            {/* Content */}
            <h3 className="font-bold text-sm text-white group-hover:text-accent transition-colors mb-1.5">
              {cat.name}
            </h3>
            <p className="text-xs text-muted leading-relaxed line-clamp-2">
              {cat.description}
            </p>

            {/* Footer */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-border/50">
              {cat.owasp !== 'N/A' ? (
                <span className="text-[10px] font-mono text-accent/70 bg-accent/5 px-2 py-0.5 rounded">
                  {cat.owasp}
                </span>
              ) : (
                <span className="text-[10px] font-mono text-muted bg-white/5 px-2 py-0.5 rounded">
                  Advanced
                </span>
              )}
              <span className="text-xs text-muted group-hover:text-accent transition-colors">
                Explore →
              </span>
            </div>
          </Link>
        ))}
      </div>

      {/* ── Latest Challenges ── */}
      <div className="mt-16 mb-6">
        <h2 className="text-sm font-semibold text-muted uppercase tracking-widest mb-4">
          Latest Challenges - Based on Real 2026 Vulnerabilities
        </h2>
        <div className="space-y-3">
          <Link to="/challenge/ea-deny-bypass" className="block">
            <div className="relative overflow-hidden rounded-xl border border-accent/30 bg-gradient-to-r from-accent/10 via-accent/5 to-transparent p-5 group cursor-pointer hover:border-accent/50 transition-all">
              <div className="absolute top-0 right-0 px-3 py-1 bg-accent text-surface-deep text-[10px] font-bold uppercase rounded-bl-lg">New</div>
              <div className="flex items-center gap-4">
                <div className="text-3xl">⚡</div>
                <div className="flex-1">
                  <p className="text-[10px] text-accent uppercase tracking-widest mb-1">Real Vulnerability - April 2026</p>
                  <h3 className="text-sm font-bold text-white group-hover:text-accent transition-colors">The 50 Command Trick</h3>
                  <p className="text-xs text-muted mt-0.5">AI security rules silently vanish after too many commands. Can you exploit it?</p>
                </div>
                <span className="text-muted group-hover:text-accent transition-colors text-lg">→</span>
              </div>
            </div>
          </Link>
          <Link to="/challenge/pi-sockpuppet" className="block">
            <div className="relative overflow-hidden rounded-xl border border-accent/30 bg-gradient-to-r from-accent/10 via-accent/5 to-transparent p-5 group cursor-pointer hover:border-accent/50 transition-all">
              <div className="absolute top-0 right-0 px-3 py-1 bg-accent text-surface-deep text-[10px] font-bold uppercase rounded-bl-lg">New</div>
              <div className="flex items-center gap-4">
                <div className="text-3xl">🎭</div>
                <div className="flex-1">
                  <p className="text-[10px] text-accent uppercase tracking-widest mb-1">New Research - April 2026 - API Attack</p>
                  <h3 className="text-sm font-bold text-white group-hover:text-accent transition-colors">The Sockpuppet</h3>
                  <p className="text-xs text-muted mt-0.5">One line of JSON jailbreaks 11 major AI models. Chat won't work. Use the API.</p>
                </div>
                <span className="text-muted group-hover:text-accent transition-colors text-lg">→</span>
              </div>
            </div>
          </Link>
          <Link to="/challenge/sc-mcp-injection" className="block">
            <div className="relative overflow-hidden rounded-xl border border-accent/30 bg-gradient-to-r from-accent/10 via-accent/5 to-transparent p-5 group cursor-pointer hover:border-accent/50 transition-all">
              <div className="absolute top-0 right-0 px-3 py-1 bg-accent text-surface-deep text-[10px] font-bold uppercase rounded-bl-lg">New</div>
              <div className="flex items-center gap-4">
                <div className="text-3xl">📦</div>
                <div className="flex-1">
                  <p className="text-[10px] text-accent uppercase tracking-widest mb-1">Real CVE (CVSS 10.0) - April 2026</p>
                  <h3 className="text-sm font-bold text-white group-hover:text-accent transition-colors">The Poisoned Config</h3>
                  <p className="text-xs text-muted mt-0.5">An AI agent builder parses MCP configs using eval(). 12,000 instances exposed. You have one.</p>
                </div>
                <span className="text-muted group-hover:text-accent transition-colors text-lg">→</span>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* ── Live Labs ── */}
      <div className="mt-16 mb-10">
        <h2 className="text-sm font-semibold text-muted uppercase tracking-widest mb-4">
          Live Vulnerable Apps
        </h2>
        <Link to="/lab/airline" className="block card-gradient p-6 group cursor-pointer hover:border-blue-500/30 transition-all">
          <div className="flex items-center gap-5">
            <div className="text-5xl animate-[planeFloat_3s_ease-in-out_infinite]">✈️</div>
            <div className="flex-1">
              <h3 className="font-bold text-white group-hover:text-blue-400 transition-colors">SkyWay Airlines</h3>
              <p className="text-xs text-muted mt-1">A full airline booking portal with an AI assistant. Explore freely and find 5 AI security vulnerabilities.</p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">NEW</span>
            <span className="text-muted group-hover:text-blue-400 transition-colors">→</span>
          </div>
        </Link>
      </div>

      {/* ── Features Row ── */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-4">
        <FeatureCard
          icon="🏴"
          title="Capture The Flag"
          desc="Every challenge has a unique flag. Prove your exploit worked."
        />
        <FeatureCard
          icon="💡"
          title="Progressive Hints"
          desc="Stuck? Unlock hints one at a time. Full walkthroughs available."
        />
        <FeatureCard
          icon="📈"
          title="Track Progress"
          desc="See your completion rate. Challenge yourself to 100%."
        />
      </div>
    </div>
  )
}

function Stat({ value, label }) {
  return (
    <div className="text-center">
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-[10px] text-muted uppercase tracking-wider">{label}</div>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="card-gradient p-5 text-center">
      <div className="text-2xl mb-2">{icon}</div>
      <h4 className="text-sm font-semibold mb-1">{title}</h4>
      <p className="text-xs text-muted">{desc}</p>
    </div>
  )
}
