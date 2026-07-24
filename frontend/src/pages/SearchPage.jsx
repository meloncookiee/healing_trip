import { useState } from 'react'
import { Link } from 'react-router-dom'
import { searchAll } from '../api'
import { EmptyState, ErrorState, Loading } from '../components/Status'

function typeLabel(type) {
  if (type === 'temple') return '템플스테이'
  if (type === 'concert') return '공연'
  return '관광'
}

function itemPath(item) {
  if (item.type === 'temple') return `/temples/${item.id}`
  if (item.type === 'concert') return `/concerts/${item.id}`
  return `/attractions/${item.id}`
}

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  async function onSubmit(event) {
    event.preventDefault()
    const keyword = q.trim()
    if (!keyword) return

    setLoading(true)
    setError('')
    setSearched(true)
    try {
      const data = await searchAll(keyword)
      setItems(data.items || [])
    } catch (err) {
      setError(err.message || '검색에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <h1>검색</h1>
        <p className="lede">사찰명·관광지명·공연명으로 찾아보세요.</p>
      </div>

      <form className="filter-bar" onSubmit={onSubmit}>
        <input
          type="search"
          placeholder="키워드 입력"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button type="submit" className="btn">
          검색
        </button>
      </form>

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={() => onSubmit({ preventDefault() {} })} />}
      {!loading && !error && searched && items.length === 0 && (
        <EmptyState message="검색 결과가 없습니다." />
      )}
      {!loading && !error && items.length > 0 && (
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
      )}
    </section>
  )
}
