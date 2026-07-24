import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getJobs } from '../api'
import { DdayBadge, REGIONS } from '../components/DdayBadge'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function JobsPage() {
  const [q, setQ] = useState('')
  const [region, setRegion] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load(next = {}) {
    const search = next.q !== undefined ? next.q : q
    const selectedRegion = next.region !== undefined ? next.region : region
    setLoading(true)
    setError('')
    try {
      const data = await getJobs({
        q: search.trim() || undefined,
        region: selectedRegion || undefined,
      })
      setItems(data.items || [])
    } catch (err) {
      setError(err.message || '채용 목록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load({ q: '', region: '' })
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
      <h1 className="page-title">채용 정보</h1>
      <p className="page-desc">지역 필터와 키워드로 채용공고를 찾을 수 있습니다.</p>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="예: 병원, 보건, 개발"
          aria-label="채용 검색어"
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
        <EmptyState message="채용 데이터가 없습니다. POST /jobs/sync 후 다시 확인하세요." />
      )}
      {!loading && !error && items.length > 0 && (
        <ul className="card-list">
          {items.map((job) => (
            <li key={job.id} className="card-item">
              <Link to={`/jobs/${job.id}`}>
                <div className="card-top">
                  <strong>{job.title}</strong>
                  <DdayBadge item={job} />
                </div>
                <span className="meta">
                  {job.company} · {job.job_field || '직무미상'} · {job.region || '지역미상'}
                </span>
                <span className="meta">
                  {job.employment_type || '고용형태미상'}
                  {job.deadline ? ` · 마감 ${job.deadline}` : ''}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
