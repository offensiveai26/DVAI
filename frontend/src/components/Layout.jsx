import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const location = useLocation()
  const isHome = location.pathname === '/'

  return (
    <div className="min-h-screen bg-surface-deep bg-grid scanlines flex flex-col">
      {/* Ambient glow blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-accent/5 rounded-full blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-accent/3 rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border/50 backdrop-blur-md bg-surface-deep/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 flex items-center justify-center rounded-lg bg-accent/10 border border-accent/20 group-hover:glow-accent transition-shadow overflow-hidden">
              <img src="/logo.svg" alt="DVAI" className="w-9 h-9" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-accent text-glow tracking-tight">DVAI</h1>
              <p className="text-[10px] text-muted tracking-widest uppercase">Damn Vulnerable AI</p>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            <NavLink to="/" active={isHome}>Dashboard</NavLink>
            <a
              href="https://owasp.org/www-project-top-10-for-large-language-model-applications/"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 text-xs text-muted hover:text-white rounded-md hover:bg-white/5 transition-colors"
            >
              OWASP Top 10 ↗
            </a>
          </nav>
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        {children}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/30 px-6 py-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          <p className="text-xs text-muted/60">
            ⚠️ DVAI is intentionally vulnerable - for educational purposes only
          </p>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted/40">Developed & Designed by</span>
            <span className="text-xs font-semibold text-accent/70">Vivek Trivedi</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

function NavLink({ to, active, children }) {
  return (
    <Link
      to={to}
      className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
        active
          ? 'text-accent bg-accent/10'
          : 'text-muted hover:text-white hover:bg-white/5'
      }`}
    >
      {children}
    </Link>
  )
}
