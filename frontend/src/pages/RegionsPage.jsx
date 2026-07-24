import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPolicies } from '../api'
import { DdayBadge, REGIONS } from '../components/DdayBadge'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function RegionsPage() {
  const [region, setRegion] = useState('서울')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load(selected = region) {
    setLoading(true)
    setError('')
    try {
      const data = await getPolicies({ region: selected })
      setItems(data.items || [])
    } catch (err) {
      setError(err.message || '지역 혜택을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load('서울')
  }, [])

  function handleSelect(next) {
    setRegion(next)
    load(next)
  }

  return (
    <div className="page">
      <h1 className="page-title">지역별 혜택</h1>
      <p className="page-desc">시/도를 선택하면 해당 지역 정책·혜택 목록을 보여 줍니다.</p>

      <div className="chip-row" role="list">
        {REGIONS.map((r) => (
          <button
            key={r}
            type="button"
            className={r === region ? 'chip active' : 'chip'}
            onClick={() => handleSelect(r)}
          >
            {r}
          </button>
        ))}
      </div>

      {loading && <Loading />}
      {!loading && error && <ErrorState message={error} onRetry={() => load(region)} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message={`${region} 지역 데이터가 없습니다. 정책 sync 후 다시 확인하세요.`} />
      )}
      {!loading && !error && items.length > 0 && (
        <ul className="card-list">
          {items.map((policy) => (
            <li key={policy.id} className="card-item">
              <Link to={`/policies/${policy.id}`}>
                <div className="card-top">
                  <strong>{policy.title}</strong>
                  <DdayBadge item={policy} />
                </div>
                <span className="meta">
                  {policy.category || '분류미상'} · {policy.organization || '기관미상'}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
