import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPolicies } from '../api'
import { DdayBadge, REGIONS } from '../components/DdayBadge'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function PoliciesPage() {
  const [q, setQ] = useState('')
  const [region, setRegion] = useState('')
  const [category, setCategory] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load(next = {}) {
    const search = next.q !== undefined ? next.q : q
    const selectedRegion = next.region !== undefined ? next.region : region
    const selectedCategory = next.category !== undefined ? next.category : category
    setLoading(true)
    setError('')
    try {
      const data = await getPolicies({
        q: search.trim() || undefined,
        region: selectedRegion || undefined,
        category: selectedCategory.trim() || undefined,
      })
      setItems(data.items || [])
    } catch (err) {
      setError(err.message || '정책 목록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load({ q: '', region: '', category: '' })
  }, [])

  function handleSearch(e) {
    e.preventDefault()
    load()
  }

  function handleRegion(next) {
    setRegion(next)
    load({ region: next })
  }

  return (
    <div className="page">
      <h1 className="page-title">청년 정책</h1>
      <p className="page-desc">지역·분야 필터와 키워드로 정책을 찾을 수 있습니다.</p>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="예: 취업, 주거, 창업"
          aria-label="정책 검색어"
        />
        <input
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="분야 (선택)"
          aria-label="분야 필터"
        />
        <button className="btn btn-primary" type="submit">
          검색
        </button>
      </form>

      <div className="chip-row" role="list">
        <button
          type="button"
          className={!region ? 'chip active' : 'chip'}
          onClick={() => handleRegion('')}
        >
          전체
        </button>
        {REGIONS.map((r) => (
          <button
            key={r}
            type="button"
            className={r === region ? 'chip active' : 'chip'}
            onClick={() => handleRegion(r)}
          >
            {r}
          </button>
        ))}
      </div>

      {loading && <Loading />}
      {!loading && error && <ErrorState message={error} onRetry={() => load()} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message="검색 결과가 없습니다. 백엔드에서 정책 sync 후 다시 시도하세요." />
      )}
      {!loading && !error && items.length > 0 && (
        <ul className="card-list">
          {items.map((policy) => (
            <li key={policy.id} className="card-item">
              <Link to={`/policies/${policy.id}`}>
                <div className="card-top">
                  <strong>{policy.title || '제목 없음'}</strong>
                  <DdayBadge item={policy} />
                </div>
                <span className="meta">
                  {policy.organization || '기관미상'} · {policy.region || '전국'} ·{' '}
                  {policy.category || '분야미상'}
                </span>
                {policy.apply_period && (
                  <span className="meta">신청기간: {policy.apply_period}</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
