import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchChallenges, fetchCategories } from '../api'

const DIFF = {
  1: { label: 'Easy', class: 'badge-easy', stars: '⭐' },
  2: { label: 'Medium', class: 'badge-medium', stars: '⭐⭐' },
  3: { label: 'Hard', class: 'badge-hard', stars: '⭐⭐⭐' },
}

export default function CategoryPage() {
  const { categoryId } = useParams()
  const [challenges, setChallenges] = useState([])
  const [category, setCategory] = useState(null)

  useEffect(() => {
    fetchChallenges(categoryId).then(setChallenges).catch(() => {})
    fetchCategories().then((cats) => {
      setCategory(cats.find((c) => c.id === categoryId))
    }).catch(() => {})
  }, [categoryId])

  return (
    <div>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-muted mb-8">
        <Link to="/" className="hover:text-white transition-colors">Dashboard</Link>
        <span>/</span>
        <span className="text-white">{category?.name || '...'}</span>
      </div>

      {/* Category Header */}
      {category && (
        <div className="card-gradient p-8 mb-8">
          <div className="flex items-start gap-5">
            <div className="w-16 h-16 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0">
              <span className="text-3xl">{category.icon}</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">{category.name}</h1>
              <p className="text-muted text-sm mb-3">{category.description}</p>
              <div className="flex items-center gap-3">
                {category.owasp !== 'N/A' && (
                  <span className="text-xs font-mono text-accent bg-accent/10 px-2.5 py-1 rounded-md border border-accent/20">
                    OWASP {category.owasp}
                  </span>
                )}
                <span className="text-xs text-muted">
                  {challenges.length} challenge{challenges.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Challenge List */}
      <div className="space-y-3">
        {challenges.map((ch, i) => {
          const d = DIFF[ch.difficulty]
          return (
            <Link
              key={ch.id}
              to={`/challenge/${ch.id}`}
              className="block card-gradient category-card p-5"
            >
              <div className="flex items-center gap-4">
                {/* Number */}
                <div className="w-10 h-10 rounded-lg bg-border flex items-center justify-center shrink-0">
                  <span className="text-sm font-mono text-muted">{String(i + 1).padStart(2, '0')}</span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm text-white group-hover:text-accent">
                    {ch.name}
                  </h3>
                  <p className="text-xs text-muted mt-0.5 truncate">{ch.description}</p>
                </div>

                {/* Difficulty */}
                <div className={`px-3 py-1 rounded-full text-xs font-medium shrink-0 ${d.class}`}>
                  {d.label}
                </div>

                {/* Arrow */}
                <span className="text-muted text-sm">→</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
