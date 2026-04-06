/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        accent: { DEFAULT: '#00ff88', dim: '#00cc6a', muted: 'rgba(0,255,136,0.1)' },
        danger: { DEFAULT: '#ff4757', muted: 'rgba(255,71,87,0.1)' },
        warning: { DEFAULT: '#ffa502', muted: 'rgba(255,165,2,0.1)' },
        surface: {
          deep: '#050508',
          base: '#0a0a0f',
          card: '#0f0f18',
          elevated: '#14141f',
        },
        border: { DEFAULT: '#1a1a2e', bright: '#2a2a3e' },
        muted: '#6b6b80',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
