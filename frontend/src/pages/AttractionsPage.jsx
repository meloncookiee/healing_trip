import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAttractions } from '../api'
import PlacesMap from '../components/PlacesMap'
import { EmptyState, ErrorState, Loading } from '../components/Status'

const CATEGORIES = [
  { value: '', label: '전체' },
  { value: '관광지', label: '관광지' },
  { value: '관광단지', label: '관광단지' },
  { value: '가이드북', label: '가이드북' },
]

export default function AttractionsPage() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const linkFor = useRef((item) => `/attractions/${item.id}`).current

  async function load({ keyword = q, cat = category } = {}) {
    setLoading(true)
    setError('')
    try {
      const data = await getAttractions({
        q: keyword.trim() || undefined,
        category: cat || undefined,
        limit: 100,
      })
      setItems(data.items || [])
      setTotal(data.total || 0)
    } catch (err) {
      setError(err.message || '목록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load({ keyword: '', cat: '' })
  }, [])

  function onSubmit(event) {
    event.preventDefault()
    load()
  }

  return (
    <section className="page">
      <div className="page-header">
        <h1>경기도 자연관광</h1>
        <p className="lede">지도와 목록으로 경기도 관광지·단지를 찾아보세요.</p>
      </div>

      <form className="filter-bar" onSubmit={onSubmit}>
        <input
          type="search"
          placeholder="관광지명·지역 검색"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          value={category}
          onChange={(e) => {
            const next = e.target.value
            setCategory(next)
            load({ cat: next })
          }}
        >
          {CATEGORIES.map((opt) => (
            <option key={opt.value || 'all'} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <button type="submit" className="btn">
          검색
        </button>
      </form>

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={() => load()} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message="조건에 맞는 관광 정보가 없습니다." />
      )}
      {!loading && !error && items.length > 0 && (
        <>
          <PlacesMap
            places={items}
            title="자연관광 지도"
            listPath="/attractions"
            label="관광지"
            linkFor={linkFor}
          />
          <p className="meta" style={{ marginTop: '1.25rem' }}>
            총 {total}건
          </p>
          <ul className="card-list temple-card-list">
            {items.map((item) => (
              <li key={item.id} className="card-item temple-card">
                <Link to={`/attractions/${item.id}`}>
                  <img
                    className="card-thumb"
                    src={item.image_url}
                    alt=""
                    onError={(e) => {
                      e.currentTarget.src =
                        'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80'
                    }}
                  />
                  <div className="card-body">
                    <h2>{item.name}</h2>
                    <p>{item.address || '위치 정보 없음'}</p>
                    <p className="meta">
                      {[item.category, item.region || item.sigungu]
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
