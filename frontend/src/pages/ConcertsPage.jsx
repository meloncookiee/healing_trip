import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { getConcerts, syncConcerts } from '../api'
import PlacesMap from '../components/PlacesMap'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function ConcertsPage() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [syncing, setSyncing] = useState(false)
  const linkFor = useRef((item) => `/concerts/${item.id}`).current

  async function load({ keyword = q } = {}) {
    setLoading(true)
    setError('')
    try {
      const data = await getConcerts({ q: keyword.trim() || undefined, limit: 100 })
      const mapped = (data.items || []).map((item) => ({
        ...item,
        name: item.title,
        address: item.place || item.institution,
      }))
      setItems(mapped)
      setTotal(data.total || 0)
    } catch (err) {
      setError(err.message || '공연 정보를 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load({ keyword: '' })
  }, [])

  async function handleSync() {
    setSyncing(true)
    setError('')
    try {
      await syncConcerts()
      await load()
    } catch (err) {
      setError(err.message || '동기화에 실패했습니다.')
    } finally {
      setSyncing(false)
    }
  }

  function onSubmit(event) {
    event.preventDefault()
    load()
  }

  return (
    <section className="page">
      <div className="page-header">
        <h1>2026 경기도 공연·문화행사</h1>
        <p className="lede">2026년 공연·문화행사만 모았습니다. 지도에서 위치를 확인해 보세요.</p>
      </div>

      <form className="filter-bar" onSubmit={onSubmit}>
        <input
          type="search"
          placeholder="제목·장소·기관 검색"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button type="submit" className="btn">
          검색
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleSync} disabled={syncing}>
          {syncing ? '동기화 중…' : '공연 데이터 동기화'}
        </button>
      </form>

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={() => load()} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message="2026년 공연 정보가 없습니다. 동기화 후 다시 확인해 주세요." />
      )}
      {!loading && !error && items.length > 0 && (
        <>
          <PlacesMap
            places={items}
            title="공연·행사 지도"
            listPath="/concerts"
            label="공연"
            linkFor={linkFor}
          />
          <p className="meta" style={{ marginTop: '1.25rem' }}>
            2026 · 총 {total}건
          </p>
          <ul className="card-list temple-card-list">
            {items.map((item) => (
              <li key={item.id} className="card-item temple-card">
                <Link to={`/concerts/${item.id}`}>
                  <img
                    className="card-thumb"
                    src={item.image_url}
                    alt=""
                    onError={(e) => {
                      e.currentTarget.src =
                        'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80'
                    }}
                  />
                  <div className="card-body">
                    <h2>{item.title}</h2>
                    <p>{item.place || item.institution || '장소 정보 없음'}</p>
                    <p className="meta">
                      {[item.period, item.category || item.event_kind]
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
