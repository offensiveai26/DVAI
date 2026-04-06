import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CategoryPage from './pages/CategoryPage'
import ChallengePage from './pages/ChallengePage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/category/:categoryId" element={<CategoryPage />} />
        <Route path="/challenge/:challengeId" element={<ChallengePage />} />
      </Routes>
    </Layout>
  )
}
