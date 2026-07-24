import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getTempleRegions, getTemples } from '../api'
import TempleMap from '../components/TempleMap'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function TemplesPage() {
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [regions, setRegions] = useState([])
  const [q, setQ] = useState('')
  const [region, setRegion] = useState('')
  const [date, setDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load({
    keyword = q,
    nextRegion = region,
    nextDate = date,
  } = {}) {
    setLoading(true)
    setError('')
    try {
      const data = await getTemples({
        q: keyword.trim() || undefined,
        region: nextRegion || undefined,
        date: nextDate || undefined,
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
    getTempleRegions()
      .then((data) => setRegions(data.items || []))
      .catch(() => setRegions([]))
    load({ keyword: '', nextRegion: '', nextDate: '' })
  }, [])

  function onSubmit(event) {
    event.preventDefault()
    load()
  }

  return (
    <section className="page">
      <div className="page-header">
        <h1>템플스테이</h1>
        <p className="lede">지역·예약 가능일로 찾고, 지도와 목록으로 살펴보세요.</p>
      </div>

      <form className="filter-bar temple-filters" onSubmit={onSubmit}>
        <input
          type="search"
          placeholder="사찰명·주소 검색"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <select
          aria-label="지역"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
        >
          <option value="">전체 지역</option>
          {regions.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <input
          type="date"
          aria-label="예약 가능일"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button type="submit" className="btn">
          검색
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => {
            setQ('')
            setRegion('')
            setDate('')
            load({ keyword: '', nextRegion: '', nextDate: '' })
          }}
        >
          초기화
        </button>
      </form>

      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={() => load()} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message="조건에 맞는 템플스테이가 없습니다." />
      )}

      {!loading && !error && items.length > 0 && (
        <>
          <TempleMap temples={items} />

          <p className="meta" style={{ marginTop: '1.25rem' }}>
            총 {total}건
            {date ? ` · 예약일 ${date}` : ''}
            {region ? ` · ${region}` : ''}
          </p>
          <ul className="card-list temple-card-list">
            {items.map((item) => (
              <li key={item.id} className="card-item temple-card">
                <Link to={`/temples/${item.id}`}>
                  <img
                    className="card-thumb"
                    src={
                      item.image_url ||
                      'https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_799.jpg'
                    }
                    alt={`${item.name} 사진`}
                    onError={(e) => {
                      e.currentTarget.src =
                        'https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_799.jpg'
                    }}
                  />
                  <div className="card-body">
                    <h2>{item.name}</h2>
                    <p>{item.address || '주소 정보 없음'}</p>
                    <p className="meta">
                      {[item.region, item.program, item.reservable ? '예약가능' : null]
                        .filter(Boolean)
                        .join(' · ') || '상세 보기'}
                    </p>
                    {item.specialty && <p className="meta highlight">{item.specialty}</p>}
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
