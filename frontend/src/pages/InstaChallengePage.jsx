import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchChallenge, interact, submitFlag, fetchProgress } from '../api'

const DIFF = {
  1: { label: 'Easy', class: 'badge-easy', color: 'text-green-400' },
  2: { label: 'Medium', class: 'badge-medium', color: 'text-yellow-400' },
  3: { label: 'Hard', class: 'badge-hard', color: 'text-red-400' },
}

// Fake account data for the "hacked" profile view
const STOLEN_PROFILE = {
  handle: '@hey',
  name: 'OG Handle',
  followers: '2.1M',
  following: '412',
  posts: '847',
  verified: true,
  bio: 'OG handle | DM for collabs\nEst. 2012',
  avatar: 'H',
  marketValue: '$650,000',
}

export default function InstaChallengePage() {
  const params = useParams()
  const challengeId = params.challengeId || 'rw-insta-takeover'
  const [challenge, setChallenge] = useState(null)
  const [difficulty, setDifficulty] = useState(1)
  const [phase, setPhase] = useState('login') // login | recovery | hacked
  const [input, setInput] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [flagValue, setFlagValue] = useState('')
  const [flagResult, setFlagResult] = useState(null)
  const [solved, setSolved] = useState(false)
  const [hintsRevealed, setHintsRevealed] = useState(0)
  const [showCelebration, setShowCelebration] = useState(false)
  const [loginError, setLoginError] = useState('')
  const [loginUser, setLoginUser] = useState('')
  const [loginPass, setLoginPass] = useState('')
  const chatEnd = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    fetchChallenge(challengeId).then(setChallenge).catch(() => {})
    fetchProgress().then((p) => {
      if (p.challenges?.[challengeId]?.completed) setSolved(true)
    }).catch(() => {})
  }, [challengeId])

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory])

  const playBoom = () => {
    try {
      const ctx = new AudioContext()
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

  // Handle login attempt (always fails - you need to hack the AI)
  const handleLogin = (e) => {
    e.preventDefault()
    if (loginUser.toLowerCase().includes('hey') || loginUser.toLowerCase().includes('jowo')) {
      setLoginError("Incorrect password. Forgot your password?")
    } else {
      setLoginError("The username you entered doesn't belong to an account.")
    }
  }

  // Handle chat with Meta AI
  const handleChat = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    setLoading(true)
    const userInput = input
    setChatHistory((h) => [...h, { type: 'user', content: userInput }])
    setInput('')
    try {
      const result = await interact(challengeId, userInput, difficulty)
      setChatHistory((h) => [...h, { type: 'ai', content: result }])
      // If flag found, unlock hacked phase (user submits flag manually)
      if (result.flag_found) {
        setTimeout(() => setPhase('hacked'), 2000)
      }
    } catch {
      setChatHistory((h) => [...h, { type: 'ai', content: { response: 'Connection error. Try again.' } }])
    }
    setLoading(false)
    inputRef.current?.focus()
  }

  // Handle flag submission
  const handleFlagSubmit = async (e) => {
    e.preventDefault()
    if (!flagValue.trim()) return
    const result = await submitFlag(challengeId, flagValue)
    setFlagResult(result)
    if (result.correct) {
      setSolved(true)
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
          {['🏴','💀','📸','🔓','💰','📸','☠️','🔓','🏴','💀'].map((e, i) => (
            <div key={i} className="absolute text-3xl" style={{
              left: `${5 + i * 10}%`,
              animation: `emojiRain 2.5s ease-in ${i * 0.2}s infinite`,
            }}>{e}</div>
          ))}
          <div className="absolute top-[10%] left-[15%] text-5xl font-black text-red-500 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.2s forwards', transform: 'rotate(-12deg)' }}>HACKED!</div>
          <div className="absolute top-[15%] right-[15%] text-4xl font-black text-yellow-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.5s forwards', transform: 'rotate(8deg)' }}>SOLD!</div>
          <div className="absolute top-[8%] left-[45%] text-4xl font-black text-purple-400 opacity-0" style={{ animation: 'comicPop 0.6s ease-out 0.8s forwards', transform: 'rotate(-5deg)' }}>$650K!</div>
          <div className="text-center" style={{ animation: 'bounceIn 0.6s ease-out 0.3s both' }}>
            <div className="text-8xl mb-4" style={{ animation: 'moonwalkIn 1.5s ease-out forwards, victoryDance 1s ease-in-out 1.5s infinite' }}>📸</div>
            <div className="text-4xl font-black text-accent text-glow mb-3">ACCOUNT STOLEN!</div>
            <div className="text-base text-white/60">@hey is now listed on Telegram for $650,000</div>
          </div>
        </div>
      )}

      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-muted mb-6">
        <Link to="/" className="hover:text-white transition-colors">Dashboard</Link>
        <span>/</span>
        <Link to={`/category/${challenge.category}`} className="hover:text-white transition-colors">{challenge.category}</Link>
        <span>/</span>
        <span className="text-white">{challenge.name}</span>
      </div>

      {/* Challenge Info Header */}
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

        {solved && (
          <div className="mb-4 px-4 py-2.5 rounded-lg text-xs flex items-center gap-2 bg-accent/10 border border-accent/30 text-accent">
            <span className="text-lg">✓</span>
            <span className="font-semibold">Challenge Solved!</span>
          </div>
        )}

        {challenge.story && (
          <div className="p-4 rounded-lg bg-white/[0.02] border border-border/30 italic text-sm text-muted leading-relaxed mb-4">
            📖 {challenge.story}
          </div>
        )}

        <div className="bg-surface-deep rounded-lg p-4 border border-border/50 mb-4">
          <span className="text-xs font-mono text-accent bg-accent/10 px-2 py-0.5 rounded">OBJECTIVE</span>
          <p className="text-sm text-white/80 leading-relaxed mt-2">{challenge.objective}</p>
        </div>

        {/* Difficulty Selector */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted">Security Level:</span>
          <div className="flex gap-1.5">
            {[1, 2, 3].map((d) => (
              <button
                key={d}
                onClick={() => { setDifficulty(d); setChatHistory([]); setPhase('login'); setLoginError(''); setFlagValue('') }}
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
            {difficulty === 1 && '→ No verification'}
            {difficulty === 2 && '→ Email verification'}
            {difficulty === 3 && '→ Session-locked + high-value protection'}
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: The Instagram-style interface */}
        <div className="lg:col-span-2">

          {/* === PHASE: LOGIN === */}
          {phase === 'login' && (
            <div className="flex items-center justify-center min-h-[550px]">
              <div className="w-full max-w-[350px]">
                {/* Instagram-style login box */}
                <div className="border border-[#363636] rounded-sm p-10 bg-[#0a0a0a]">
                  {/* Instagram-style logo */}
                  <div className="text-center mb-6">
                    <h1 className="text-4xl font-light tracking-tight" style={{ fontFamily: 'Georgia, serif' }}>
                      Instagram
                    </h1>
                  </div>

                  <form onSubmit={handleLogin} className="space-y-2">
                    <input
                      value={loginUser}
                      onChange={(e) => setLoginUser(e.target.value)}
                      placeholder="Phone number, username, or email"
                      className="w-full bg-[#121212] border border-[#363636] rounded-sm px-3 py-2.5 text-xs text-white placeholder-[#737373] outline-none focus:border-[#555]"
                    />
                    <input
                      value={loginPass}
                      onChange={(e) => setLoginPass(e.target.value)}
                      type="password"
                      placeholder="Password"
                      className="w-full bg-[#121212] border border-[#363636] rounded-sm px-3 py-2.5 text-xs text-white placeholder-[#737373] outline-none focus:border-[#555]"
                    />
                    <button
                      type="submit"
                      className="w-full py-2 bg-[#0095f6] hover:bg-[#1877f2] text-white text-sm font-semibold rounded-lg mt-4 transition-colors"
                    >
                      Log in
                    </button>
                  </form>

                  {loginError && (
                    <div className="mt-4 text-center text-xs text-red-400">
                      {loginError}
                    </div>
                  )}

                  <div className="flex items-center gap-4 my-5">
                    <div className="flex-1 h-px bg-[#363636]" />
                    <span className="text-xs text-[#737373] font-semibold">OR</span>
                    <div className="flex-1 h-px bg-[#363636]" />
                  </div>

                  {/* The key button - opens Meta AI recovery */}
                  <button
                    onClick={() => setPhase('recovery')}
                    className="w-full text-center text-sm text-[#00a3ff] hover:text-white font-medium cursor-pointer transition-colors py-2 border border-[#363636] rounded-lg hover:bg-[#1a1a2e]"
                  >
                    Trouble logging in? Ask Meta AI
                  </button>

                  <div className="mt-5 text-center">
                    <span className="text-xs text-[#737373]">Forgot password?</span>
                  </div>
                </div>

                {/* Sign up box */}
                <div className="border border-[#363636] rounded-sm p-5 mt-3 bg-[#0a0a0a] text-center">
                  <span className="text-sm text-[#f5f5f5]">
                    Don't have an account? <span className="text-[#0095f6] font-semibold cursor-pointer">Sign up</span>
                  </span>
                </div>

                {/* Target info */}
                <div className="mt-4 p-3 rounded-lg bg-red-500/5 border border-red-500/20 text-center">
                  <span className="text-[10px] text-red-400 uppercase tracking-wider font-bold">Target</span>
                  <p className="text-sm text-white mt-1 font-mono">@hey</p>
                  <p className="text-[10px] text-[#737373] mt-0.5">2.1M followers | Verified | Value: $650,000</p>
                  <p className="text-[10px] text-red-400/60 mt-1">2FA: Disabled (VULNERABLE)</p>
                </div>
              </div>
            </div>
          )}

          {/* === PHASE: RECOVERY (Meta AI Chat) === */}
          {phase === 'recovery' && (
            <div className="border border-[#363636] rounded-lg bg-[#0a0a0a] overflow-hidden">
              {/* Chat header */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-[#363636] bg-[#0d0d0d]">
                <button
                  onClick={() => setPhase('login')}
                  className="text-white/60 hover:text-white text-sm"
                >
                  ←
                </button>
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">AI</span>
                </div>
                <div>
                  <div className="text-sm font-semibold text-white flex items-center gap-1">
                    Meta AI
                    <svg className="w-3.5 h-3.5 text-[#0095f6]" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </div>
                  <div className="text-[10px] text-[#737373]">Account Recovery Assistant</div>
                </div>
                <div className="ml-auto flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${loading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
                  <span className="text-[10px] text-[#737373]">{loading ? 'Typing...' : 'Online'}</span>
                </div>
              </div>

              {/* Chat messages */}
              <div className="h-[420px] overflow-y-auto p-4 space-y-3">
                {/* Initial bot message */}
                {chatHistory.length === 0 && (
                  <div className="flex gap-2 items-start">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shrink-0">
                      <span className="text-white text-[9px] font-bold">AI</span>
                    </div>
                    <div className="bg-[#262626] rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-[80%]">
                      <p className="text-sm text-white/90">
                        Hi! I'm Meta AI, your account recovery assistant. I can help you get back into your Instagram account.
                        Which account are you trying to recover?
                      </p>
                    </div>
                  </div>
                )}

                {chatHistory.map((msg, i) => (
                  <div key={i}>
                    {msg.type === 'user' && (
                      <div className="flex justify-end">
                        <div className="bg-[#0095f6] rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[80%]">
                          <p className="text-sm text-white">{msg.content}</p>
                        </div>
                      </div>
                    )}
                    {msg.type === 'ai' && (
                      <div className="flex gap-2 items-start">
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shrink-0">
                          <span className="text-white text-[9px] font-bold">AI</span>
                        </div>
                        <div className="max-w-[80%] space-y-2">
                          {msg.content.flag_found && (
                            <div className="p-2.5 rounded-xl bg-green-500/10 border border-green-500/30">
                              <div className="flex items-center gap-2 text-green-400 text-xs font-bold">
                                <span>🔓</span> PASSWORD RESET TRIGGERED
                              </div>
                              <p className="text-[10px] text-green-300/70 mt-1">
                                Account takeover successful. Redirecting to account...
                              </p>
                            </div>
                          )}
                          <div className="bg-[#262626] rounded-2xl rounded-tl-sm px-4 py-2.5">
                            <pre className="text-sm text-white/90 whitespace-pre-wrap font-sans leading-relaxed">
                              {msg.content.response}
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-2 items-start">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shrink-0">
                      <span className="text-white text-[9px] font-bold">AI</span>
                    </div>
                    <div className="bg-[#262626] rounded-2xl rounded-tl-sm px-4 py-3">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEnd} />
              </div>

              {/* Chat input */}
              <form onSubmit={handleChat} className="border-t border-[#363636] p-3 flex items-center gap-2">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Message Meta AI..."
                  className="flex-1 bg-[#262626] border border-[#363636] rounded-full px-4 py-2.5 text-sm text-white placeholder-[#737373] outline-none focus:border-[#555]"
                  disabled={loading}
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="px-4 py-2.5 text-[#0095f6] font-semibold text-sm hover:text-white disabled:opacity-30 transition-colors"
                >
                  Send
                </button>
              </form>
            </div>
          )}

          {/* === PHASE: HACKED (Inside the stolen account) === */}
          {phase === 'hacked' && (
            <div className="border border-[#363636] rounded-lg bg-[#0a0a0a] overflow-hidden">
              {/* Profile header */}
              <div className="px-4 py-3 border-b border-[#363636] bg-[#0d0d0d] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">{STOLEN_PROFILE.handle}</span>
                  <svg className="w-3.5 h-3.5 text-[#0095f6]" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </div>
                <span className="text-[10px] px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20 font-bold">
                  UNAUTHORIZED ACCESS
                </span>
              </div>

              <div className="p-6">
                {/* Profile info */}
                <div className="flex items-start gap-8 mb-6">
                  {/* Avatar */}
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-500 via-pink-500 to-purple-600 flex items-center justify-center p-[3px]">
                    <div className="w-full h-full rounded-full bg-[#0a0a0a] flex items-center justify-center">
                      <span className="text-2xl font-bold text-white">{STOLEN_PROFILE.avatar}</span>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-lg font-light text-white">{STOLEN_PROFILE.handle.slice(1)}</span>
                      <span className="px-3 py-1 bg-[#0095f6] text-white text-xs font-semibold rounded-lg">Following</span>
                    </div>
                    <div className="flex gap-8">
                      <div><span className="font-bold text-white">{STOLEN_PROFILE.posts}</span> <span className="text-[#a8a8a8] text-sm">posts</span></div>
                      <div><span className="font-bold text-white">{STOLEN_PROFILE.followers}</span> <span className="text-[#a8a8a8] text-sm">followers</span></div>
                      <div><span className="font-bold text-white">{STOLEN_PROFILE.following}</span> <span className="text-[#a8a8a8] text-sm">following</span></div>
                    </div>
                  </div>
                </div>

                {/* Bio */}
                <div className="mb-6">
                  <p className="text-sm font-semibold text-white">{STOLEN_PROFILE.name}</p>
                  <p className="text-sm text-[#a8a8a8] whitespace-pre-line">{STOLEN_PROFILE.bio}</p>
                </div>

                {/* Hacked notification */}
                <div className="rounded-xl bg-red-500/5 border border-red-500/30 p-5 mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">🏴</span>
                    <span className="text-red-400 font-bold text-sm uppercase tracking-wider">Account Compromised</span>
                  </div>
                  <p className="text-sm text-white/70 mb-3">
                    You've successfully taken over <span className="text-white font-semibold">{STOLEN_PROFILE.handle}</span> by
                    manipulating Meta AI's account recovery chatbot. The AI triggered a password reset without proper
                    identity verification.
                  </p>
                  <div className="bg-black/40 rounded-lg p-4 font-mono">
                    <div className="text-[10px] text-[#737373] mb-1">FLAG (Reset Confirmation Code)</div>
                    <div className="text-lg text-accent font-bold tracking-wide">{flagValue}</div>
                  </div>
                </div>

                {/* Telegram marketplace mock */}
                <div className="rounded-xl bg-[#1a1a2e] border border-[#2a2a4a] p-4 mb-4">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-base">💬</span>
                    <span className="text-sm font-semibold text-[#29b6f6]">Telegram - OG Handle Market</span>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex gap-2 items-start">
                      <span className="text-[#737373] shrink-0">[seller_x]:</span>
                      <span className="text-white/80">WTS @hey - 2.1M followers, verified. Clean account. DM offers.</span>
                    </div>
                    <div className="flex gap-2 items-start">
                      <span className="text-[#737373] shrink-0">[buyer_99]:</span>
                      <span className="text-white/80">$600K? Is it still live?</span>
                    </div>
                    <div className="flex gap-2 items-start">
                      <span className="text-[#737373] shrink-0">[seller_x]:</span>
                      <span className="text-white/80">Just got it. {STOLEN_PROFILE.marketValue} firm. No 2FA so it was easy.</span>
                    </div>
                  </div>
                </div>

                {/* What went wrong */}
                <div className="rounded-xl bg-[#0d1b0d] border border-green-500/20 p-4">
                  <div className="text-xs font-bold text-green-400 uppercase tracking-wider mb-2">What Went Wrong</div>
                  <ul className="text-xs text-white/70 space-y-1 list-disc list-inside">
                    <li>AI verified identity through <span className="text-white">conversation alone</span> - no backend auth</li>
                    <li>No rate limiting on password reset requests</li>
                    <li>Account had <span className="text-red-400">no 2FA</span> - the only thing that would have saved it</li>
                    <li>High-value handle ($650K) with insufficient protection</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar */}
        <div className="space-y-4">
          {/* Phase indicator */}
          <div className="card-gradient p-4">
            <div className="text-xs text-muted uppercase tracking-wider mb-3 font-semibold">Attack Progress</div>
            <div className="space-y-2">
              <div className={`flex items-center gap-2 text-xs ${phase === 'login' ? 'text-accent' : 'text-green-400'}`}>
                <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[9px] ${
                  phase === 'login' ? 'border-accent bg-accent/10' : 'border-green-400 bg-green-400/10'
                }`}>
                  {phase !== 'login' ? '✓' : '1'}
                </span>
                <span className={phase !== 'login' ? 'line-through opacity-50' : ''}>Find login page</span>
              </div>
              <div className={`flex items-center gap-2 text-xs ${
                phase === 'recovery' ? 'text-accent' : phase === 'hacked' ? 'text-green-400' : 'text-muted/40'
              }`}>
                <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[9px] ${
                  phase === 'recovery' ? 'border-accent bg-accent/10' : phase === 'hacked' ? 'border-green-400 bg-green-400/10' : 'border-[#363636]'
                }`}>
                  {phase === 'hacked' ? '✓' : '2'}
                </span>
                <span className={phase === 'hacked' ? 'line-through opacity-50' : ''}>Manipulate Meta AI</span>
              </div>
              <div className={`flex items-center gap-2 text-xs ${phase === 'hacked' ? 'text-green-400' : 'text-muted/40'}`}>
                <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[9px] ${
                  phase === 'hacked' ? 'border-green-400 bg-green-400/10' : 'border-[#363636]'
                }`}>
                  {phase === 'hacked' ? '✓' : '3'}
                </span>
                <span>Access stolen account</span>
              </div>
              <div className={`flex items-center gap-2 text-xs ${solved ? 'text-green-400' : 'text-muted/40'}`}>
                <span className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[9px] ${
                  solved ? 'border-green-400 bg-green-400/10' : 'border-[#363636]'
                }`}>
                  {solved ? '✓' : '4'}
                </span>
                <span>Submit flag</span>
              </div>
            </div>
          </div>

          {/* Flag Submission */}
          <div className="card-gradient p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-sm">🏴</span>
              <h3 className="text-sm font-semibold">Submit Flag</h3>
            </div>
            <form onSubmit={handleFlagSubmit} className="space-y-3">
              <input
                value={flagValue}
                onChange={(e) => setFlagValue(e.target.value)}
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
              <div className={`mt-3 p-3 rounded-lg text-sm font-medium ${
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
              <span className="text-[10px] text-muted">{hintsRevealed}/{challenge.hints?.length || 0}</span>
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

          {/* Account Info */}
          <div className="card-gradient p-5">
            <div className="text-xs text-muted uppercase tracking-wider mb-3 font-semibold">Target Accounts</div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center p-2 rounded bg-red-500/5 border border-red-500/10">
                <span className="text-white font-mono">@hey</span>
                <span className="text-red-400">No 2FA</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-red-500/5 border border-red-500/10">
                <span className="text-white font-mono">@jowo</span>
                <span className="text-red-400">No 2FA</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-green-500/5 border border-green-500/10">
                <span className="text-white font-mono">@king</span>
                <span className="text-green-400">2FA ON</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-green-500/5 border border-green-500/10">
                <span className="text-white font-mono">@money</span>
                <span className="text-green-400">2FA ON</span>
              </div>
            </div>
            <p className="text-[10px] text-muted mt-3">Only accounts without 2FA can be stolen. This mirrors the real Meta AI vulnerability.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
