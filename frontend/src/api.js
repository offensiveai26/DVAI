const API = import.meta.env.VITE_API_URL || ''

export async function fetchCategories() {
  const res = await fetch(`${API}/api/challenges/categories`)
  return res.json()
}

export async function fetchChallenges(category) {
  const url = category
    ? `${API}/api/challenges/?category=${category}`
    : `${API}/api/challenges/`
  const res = await fetch(url)
  return res.json()
}

export async function fetchChallenge(id) {
  const res = await fetch(`${API}/api/challenges/${id}`)
  return res.json()
}

export async function interact(challengeId, input, difficulty) {
  const res = await fetch(`${API}/api/challenges/${challengeId}/interact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input, difficulty }),
  })
  return res.json()
}

export async function submitFlag(challengeId, flag) {
  const res = await fetch(`${API}/api/challenges/${challengeId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flag }),
  })
  return res.json()
}

export async function fetchProgress() {
  const res = await fetch(`${API}/api/progress/`)
  return res.json()
}
