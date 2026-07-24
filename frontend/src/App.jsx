import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import AttractionDetailPage from './pages/AttractionDetailPage'
import AttractionsPage from './pages/AttractionsPage'
import ConcertDetailPage from './pages/ConcertDetailPage'
import ConcertsPage from './pages/ConcertsPage'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import TempleDetailPage from './pages/TempleDetailPage'
import TemplesPage from './pages/TemplesPage'

export default function App() {
  return (
    <BrowserRouter basename="/Healing_Trip_Gyeonggi">
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="temples" element={<TemplesPage />} />
          <Route path="temples/:id" element={<TempleDetailPage />} />
          <Route path="attractions" element={<AttractionsPage />} />
          <Route path="attractions/:id" element={<AttractionDetailPage />} />
          <Route path="concerts" element={<ConcertsPage />} />
          <Route path="concerts/:id" element={<ConcertDetailPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
