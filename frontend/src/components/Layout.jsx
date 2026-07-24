import { NavLink, Outlet } from 'react-router-dom'
import LotusClickEffect from './LotusClickEffect'

const LINKS = [
  { to: '/', label: '홈', end: true },
  { to: '/temples', label: '템플스테이' },
  { to: '/attractions', label: '자연관광' },
  { to: '/concerts', label: '공연' },
  { to: '/search', label: '검색' },
]

export default function Layout() {
  return (
    <div className="app-shell">
      <LotusClickEffect />
      <header className="app-header">
        <div className="brand">
          <NavLink to="/" className="brand-link">
            경기도 힐링 여행
          </NavLink>
          <span className="brand-sub">템플스테이 · 자연관광 · 공연</span>
        </div>
        <nav className="app-nav" aria-label="주요 메뉴">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
