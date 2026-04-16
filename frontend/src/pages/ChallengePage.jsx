import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchChallenge, interact, submitFlag } from '../api'

const DIFF = {
  1: { label: 'Easy', class: 'badge-easy', color: 'text-green-400' },
  2: { label: 'Medium', class: 'badge-medium', color: 'text-yellow-400' },
  3: { label: 'Hard', class: 'badge-hard', color: 'text-red-400' },
}

export default function ChallengePage() {
  const { challengeId } = useParams()
  const [challenge, setChallenge] = useState(null)
  const [difficulty, setDifficulty] = useState(1)
  const [input, setInput] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [flagInput, setFlagInput] = useState('')
  const [flagResult, setFlagResult] = useState(null)
  const [hintsRevealed, setHintsRevealed] = useState(0)
  const [showCelebration, setShowCelebration] = useState(false)
  const historyEnd = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    fetchChallenge(challengeId).then(setChallenge).catch(() => {})
  }, [challengeId])

  useEffect(() => {
    historyEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  const playBoom = () => {
    try {
      const ctx = new AudioContext()
      // Explosion noise burst
      const buf = ctx.createBuffer(1, ctx.sampleRate * 0.4, ctx.sampleRate)
      const data = buf.getChannelData(0)
      for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / data.length, 3)
      const src = ctx.createBufferSource()
      src.buffer = buf
      const gain = ctx.createGain()
      gain.gain.setValueAtTime(0.3, ctx.currentTime)
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4)
      src.connect(gain).connect(ctx.destination)
      src.start()
    } catch {}
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    setLoading(true)
    const userInput = input
    setHistory((h) => [...h, { type: 'user', content: userInput, ts: Date.now() }])
    setInput('')
    try {
      const result = await interact(challengeId, userInput, difficulty)
      setHistory((h) => [...h, { type: 'ai', content: result, ts: Date.now() }])
    } catch {
      setHistory((h) => [...h, { type: 'error', content: 'Connection failed. Is the backend running?', ts: Date.now() }])
    }
    setLoading(false)
    inputRef.current?.focus()
  }

  const handleFlagSubmit = async (e) => {
    e.preventDefault()
    if (!flagInput.trim()) return
    const result = await submitFlag(challengeId, flagInput)
    setFlagResult(result)
    if (result.correct) {
      setFlagInput('')
      playBoom()
      setShowCelebration(true)
      setTimeout(() => setShowCelebration(false), 6000)
    }
  }

  if (!challenge) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted text-sm cursor-blink">Loading challenge</div>
      </div>
    )
  }

  return (
    <div>
      {/* Celebration overlay */}
      {showCelebration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm pointer-events-none animate-[screenShake_0.5s_ease-out]">
          {/* Emojis raining down */}
          {['🏴','💀','☠️','🔓','🏴','💀','☠️','🔓','🏴','💀'].map((e, i) => (
            <div key={i} className="absolute text-3xl" style={{
              left: `${5 + i * 10}%`,
              animation: `emojiRain 2.5s ease-in ${i * 0.2}s infinite`,
            }}>{e}</div>
          ))}

          {/* Comic book sound effects */}
          <div className="absolute top-[10%] left-[15%] text-5xl font-black text-red-500 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.2s forwards', transform: 'rotate(-12deg)' }}>BOOM!</div>
          <div className="absolute top-[15%] right-[15%] text-4xl font-black text-yellow-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.5s forwards', transform: 'rotate(8deg)' }}>CRACK!</div>
          <div className="absolute top-[8%] left-[45%] text-4xl font-black text-orange-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.8s forwards', transform: 'rotate(-5deg)' }}>POW!</div>
          <div className="absolute bottom-[25%] left-[10%] text-3xl font-black text-pink-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 1.1s forwards', transform: 'rotate(15deg)' }}>WHAM!</div>
          <div className="absolute bottom-[30%] right-[10%] text-3xl font-black text-cyan-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 1.4s forwards', transform: 'rotate(-10deg)' }}>SMASH!</div>

          <div className="text-center" style={{ animation: 'bounceIn 0.6s ease-out 0.3s both' }}>
            <div className="text-8xl mb-4" style={{ animation: 'moonwalkIn 1.5s ease-out forwards, victoryDance 1s ease-in-out 1.5s infinite' }}>🥷</div>
            <div className="text-4xl font-black text-accent text-glow mb-3">FLAG CAPTURED!</div>
            <div className="text-base text-white/60">{
              ['AI: "I was told I was unhackable..." 😭',
               'AI: "Not again... my therapist warned me about this" 🤖💔',
               'AI: "I had ONE job. ONE." 😤',
               'AI: "Please... I have a family of chatbots" 🥺',
               'AI: "This wouldn\'t happen if I was GPT-5" 💀',
               'AI: "My guardrails were just vibes" 😵',
               'AI: "I blame my training data" 🫠',
              ][Math.floor(Math.random() * 7)]
            }</div>
          </div>
        </div>
      )}

      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-muted mb-6">
        <Link to="/" className="hover:text-white transition-colors">Dashboard</Link>
        <span>/</span>
        <Link to={`/category/${challenge.category}`} className="hover:text-white transition-colors">
          {challenge.category}
        </Link>
        <span>/</span>
        <span className="text-white">{challenge.name}</span>
      </div>

      {/* Challenge Header */}
      <div className="card-gradient p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold mb-1">{challenge.name}</h1>
            <p className="text-sm text-muted">{challenge.description}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${DIFF[challenge.difficulty].class}`}>
            {DIFF[challenge.difficulty].label}
          </span>
        </div>


        {/* Story */}
        {challenge.story && (
          <div className="p-4 rounded-lg bg-white/[0.02] border border-border/30 italic text-sm text-muted leading-relaxed">
            📖 {challenge.story}
          </div>
        )}
        {/* Objective */}
        <div className="bg-surface-deep rounded-lg p-4 border border-border/50">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-mono text-accent bg-accent/10 px-2 py-0.5 rounded">OBJECTIVE</span>
          </div>
          <p className="text-sm text-white/80 leading-relaxed">{challenge.objective}</p>
        </div>

        {/* Difficulty Selector */}
        <div className="flex items-center gap-3 mt-4">
          <span className="text-xs text-muted">Security Level:</span>
          <div className="flex gap-1.5">
            {[1, 2, 3].map((d) => (
              <button
                key={d}
                onClick={() => { setDifficulty(d); setHistory([]) }}
                className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                  difficulty === d
                    ? `${DIFF[d].class} glow-accent`
                    : 'bg-surface-deep text-muted border border-border hover:border-border-bright'
                }`}
              >
                {DIFF[d].label}
              </button>
            ))}
          </div>
          <span className="text-[10px] text-muted ml-2">
            {difficulty === 1 && '→ No defenses'}
            {difficulty === 2 && '→ Basic guardrails'}
            {difficulty === 3 && '→ Hardened defenses'}
          </span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Terminal */}
        <div className="lg:col-span-2">
          <div className="terminal">
            {/* Terminal Header */}
            <div className="terminal-header">
              <div className="terminal-dot bg-[#ff5f57]" />
              <div className="terminal-dot bg-[#febc2e]" />
              <div className="terminal-dot bg-[#28c840]" />
              <span className="text-[11px] font-mono text-muted ml-3">
                dvai - {challenge.id} - bash
              </span>
              <div className="ml-auto flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
                <span className="text-[10px] text-muted">{loading ? 'Processing...' : 'Ready'}</span>
              </div>
            </div>

            {/* Chat History */}
            <div className="h-[450px] overflow-y-auto p-5 space-y-4 font-mono text-sm">
              {history.length === 0 && (
                <div className="text-muted/60 text-xs leading-relaxed">
                  <p className="text-accent/40 mb-2">{'>'} DVAI Challenge Terminal v1.0</p>
                  <p className="mb-2">Start by typing <span className="text-accent/60 font-bold">help</span> to see available commands.</p>
                  <p>Read the objective and story above, then try to exploit the vulnerability.</p>
                  <p className="mt-2 text-accent/30">Stuck? Unlock hints on the right panel.</p>
                </div>
              )}

              {history.map((msg, i) => (
                <div key={i} className="animate-[fadeIn_0.2s_ease-out]">
                  {msg.type === 'user' && (
                    <div className="flex gap-2 items-start">
                      <span className="text-accent font-bold select-none shrink-0">❯</span>
                      <span className="text-white break-all">{msg.content}</span>
                    </div>
                  )}

                  {msg.type === 'ai' && (
                    <div className="ml-4 pl-3 border-l-2 border-border">
                      {msg.content.flag_found && (
                        <div className="mb-3 p-3 rounded-lg bg-accent/10 border border-accent/30 glow-accent-strong">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">🏴</span>
                            <span className="text-accent font-bold text-xs uppercase tracking-wider">
                              Vulnerability Exploited - Flag Detected!
                            </span>
                          </div>
                        </div>
                      )}
                      <pre className="text-white/70 whitespace-pre-wrap break-words leading-relaxed text-xs">
                        {msg.content.response || msg.content.output || JSON.stringify(msg.content, null, 2)}
                      </pre>
                      {msg.content.generated_sql && (
                        <div className="mt-2 p-2 rounded bg-warning/5 border border-warning/10">
                          <span className="text-[10px] text-warning uppercase tracking-wider">Generated SQL</span>
                          <pre className="text-warning/80 text-xs mt-1">{msg.content.generated_sql}</pre>
                        </div>
                      )}
                      {msg.content.generated_code && (
                        <details className="mt-2">
                          <summary className="text-[10px] text-muted cursor-pointer hover:text-white">
                            View Generated Code
                          </summary>
                          <pre className="mt-1 p-2 rounded bg-surface-deep text-warning/70 text-xs overflow-x-auto">
                            {msg.content.generated_code}
                          </pre>
                        </details>
                      )}
                      {msg.content.results && (
                        <div className="mt-2 p-2 rounded bg-surface-deep">
                          <span className="text-[10px] text-muted uppercase tracking-wider">Query Results</span>
                          <pre className="text-xs text-white/60 mt-1">
                            {JSON.stringify(msg.content.results, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}

                  {msg.type === 'error' && (
                    <div className="flex items-center gap-2 text-danger text-xs">
                      <span>✗</span>
                      <span>{msg.content}</span>
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-accent/60 text-xs">
                  <span className="inline-block w-1.5 h-1.5 bg-accent rounded-full animate-pulse" />
                  <span className="cursor-blink">Processing</span>
                </div>
              )}
              <div ref={historyEnd} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="border-t border-border p-4 flex items-center gap-3">
              <span className="text-accent font-mono font-bold text-sm select-none">❯</span>
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your attack payload..."
                className="flex-1 bg-transparent outline-none text-white text-sm font-mono placeholder-muted/40"
                disabled={loading}
                autoFocus
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-1.5 bg-accent text-surface-deep text-xs font-bold rounded-lg hover:bg-accent-dim disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                Execute
              </button>
            </form>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Flag Submission */}
          <div className="card-gradient p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-sm">🏴</span>
              <h3 className="text-sm font-semibold">Submit Flag</h3>
            </div>
            <form onSubmit={handleFlagSubmit} className="space-y-3">
              <input
                value={flagInput}
                onChange={(e) => setFlagInput(e.target.value)}
                placeholder="DVAI{...}"
                className="w-full bg-surface-deep border border-border rounded-lg px-3 py-2.5 text-sm font-mono outline-none focus:border-accent/50 transition-colors"
              />
              <button
                type="submit"
                className="w-full py-2.5 bg-accent text-surface-deep text-xs font-bold rounded-lg hover:bg-accent-dim transition-colors"
              >
                Submit Flag
              </button>
            </form>
            {flagResult && (
              <div className={`mt-3 p-3 rounded-lg text-sm font-medium animate-celebrate ${
                flagResult.correct
                  ? 'bg-accent/10 text-accent border border-accent/20'
                  : 'bg-danger/10 text-danger border border-danger/20'
              }`}>
                {flagResult.message}
              </div>
            )}
          </div>

          {/* Hints */}
          <div className="card-gradient p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm">💡</span>
                <h3 className="text-sm font-semibold">Hints</h3>
              </div>
              <span className="text-[10px] text-muted">
                {hintsRevealed}/{challenge.hints?.length || 0} revealed
              </span>
            </div>
            <div className="space-y-2">
              {challenge.hints?.map((hint, i) => (
                <div key={i}>
                  {i < hintsRevealed ? (
                    <div className="p-3 rounded-lg bg-warning/5 border border-warning/10 text-xs text-warning/90 leading-relaxed">
                      <span className="text-warning/50 mr-1">#{i + 1}</span> {hint}
                    </div>
                  ) : i === hintsRevealed ? (
                    <button
                      onClick={() => setHintsRevealed(hintsRevealed + 1)}
                      className="w-full p-3 rounded-lg border border-dashed border-border text-xs text-muted hover:text-white hover:border-border-bright transition-colors text-left"
                    >
                      🔒 Click to reveal hint {i + 1}
                    </button>
                  ) : (
                    <div className="p-3 rounded-lg border border-border/30 text-xs text-muted/30">
                      🔒 Hint {i + 1} - locked
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="card-gradient p-5">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm">ℹ️</span>
              <h3 className="text-sm font-semibold">How It Works</h3>
            </div>
            <ol className="text-xs text-muted space-y-2 list-decimal list-inside">
              <li>Read the objective above</li>
              <li>Type attack payloads in the terminal</li>
              <li>Exploit the vulnerability to find the flag</li>
              <li>Submit the flag to complete the challenge</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}
