import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchAll } from '../api'
import { EmptyState, ErrorState, Loading } from '../components/Status'

function typeLabel(type) {
  if (type === 'temple') return '템플스테이'
  if (type === 'concert') return '공연'
  return '자연관광'
}

function itemPath(item) {
  if (item.type === 'temple') return `/temples/${item.id}`
  if (item.type === 'concert') return `/concerts/${item.id}`
  return `/attractions/${item.id}`
}

export default function HomePage() {
  const [q, setQ] = useState('')
  const [scope, setScope] = useState('all') // all | temple | attraction | concert
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  async function runSearch(keyword = q, nextScope = scope) {
    const text = keyword.trim()
    if (!text) return

    setLoading(true)
    setError('')
    setSearched(true)
    try {
      const data = await searchAll(text, 50)
      let next = data.items || []
      if (nextScope === 'temple') {
        next = next.filter((item) => item.type === 'temple')
      } else if (nextScope === 'attraction') {
        next = next.filter((item) => item.type === 'attraction')
      } else if (nextScope === 'concert') {
        next = next.filter((item) => item.type === 'concert')
      }
      setItems(next)
    } catch (err) {
      setError(err.message || '검색에 실패했습니다.')
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(event) {
    event.preventDefault()
    runSearch()
  }

  useEffect(() => {
    if (!searched) return
    if (!q.trim()) return
    runSearch(q, scope)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope])

  return (
    <section className="page home-page">
      <div className="home-hero">
        <div className="home-hero-overlay" />
        <div className="home-hero-content">
          <p className="home-kicker">Healing Trip Gyeonggi</p>
          <h1 className="home-title">경기도 힐링 여행</h1>
          <p className="home-lede">
            경기도 템플스테이, 자연관광, 공연·문화행사를 바로 검색해 보세요.
          </p>

          <form className="home-search" onSubmit={onSubmit}>
            <input
              type="search"
              autoFocus
              placeholder="사찰명 · 관광지명 · 공연명 · 지역명 검색"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <button type="submit" className="btn">
              검색
            </button>
          </form>

          <div className="home-scope" role="group" aria-label="검색 범위">
            <button
              type="button"
              className={scope === 'all' ? 'chip active' : 'chip'}
              onClick={() => setScope('all')}
            >
              전체
            </button>
            <button
              type="button"
              className={scope === 'temple' ? 'chip active' : 'chip'}
              onClick={() => setScope('temple')}
            >
              템플스테이
            </button>
            <button
              type="button"
              className={scope === 'attraction' ? 'chip active' : 'chip'}
              onClick={() => setScope('attraction')}
            >
              자연관광
            </button>
            <button
              type="button"
              className={scope === 'concert' ? 'chip active' : 'chip'}
              onClick={() => setScope('concert')}
            >
              공연
            </button>
          </div>

          <div className="hero-actions">
            <Link className="btn btn-secondary" to="/temples">
              템플스테이 목록
            </Link>
            <Link className="btn btn-secondary" to="/attractions">
              자연관광 목록
            </Link>
            <Link className="btn btn-secondary" to="/concerts">
              공연 목록
            </Link>
          </div>
        </div>
      </div>

      <div className="home-results">
        {loading && <Loading label="검색 중…" />}
        {error && (
          <ErrorState message={error} onRetry={() => runSearch()} />
        )}
        {!loading && !error && searched && items.length === 0 && (
          <EmptyState message="검색 결과가 없습니다. 다른 키워드로 찾아보세요." />
        )}
        {!loading && !error && items.length > 0 && (
          <>
            <p className="meta">검색 결과 {items.length}건</p>
            <ul className="card-list">
              {items.map((item) => (
                <li key={`${item.type}-${item.id}`} className="card-item">
                  <Link to={itemPath(item)}>
                    <h2>{item.name}</h2>
                    <p>{item.address || '주소 정보 없음'}</p>
                    <p className="meta">
                      {[typeLabel(item.type), item.region, item.category]
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  )
}
