import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getAttraction } from '../api'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function AttractionDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setItem(await getAttraction(id))
    } catch (err) {
      setError(err.message || '상세 정보를 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [id])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!item) return <EmptyState message="관광 정보가 없습니다." />

  return (
    <section className="page">
      <Link className="back-link" to="/attractions">
        ← 목록
      </Link>
      <div className="page-header">
        <h1>{item.name}</h1>
        <p className="lede">{item.address || '위치 정보 없음'}</p>
      </div>

      <div className="panel">
        {item.image_url && (
          <img className="detail-image" src={item.image_url} alt={item.name} />
        )}
        <dl className="kv">
          <dt>유형</dt>
          <dd>{item.category || '-'}</dd>
          <dt>설명</dt>
          <dd>{item.description || '-'}</dd>
          <dt>지역</dt>
          <dd>{[item.sido, item.sigungu].filter(Boolean).join(' ') || item.region || '-'}</dd>
          <dt>좌표</dt>
          <dd>
            {item.lat != null && item.lng != null
              ? `${item.lat}, ${item.lng}`
              : '-'}
          </dd>
          <dt>가이드북</dt>
          <dd>
            {item.guidebook_url ? (
              <a href={item.guidebook_url} target="_blank" rel="noreferrer">
                가이드북 열기
              </a>
            ) : (
              '-'
            )}
          </dd>
        </dl>
      </div>
    </section>
  )
}
