import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getConcert } from '../api'
import { EmptyState, ErrorState, Loading } from '../components/Status'

export default function ConcertDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setItem(await getConcert(id))
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
  if (!item) return <EmptyState message="공연 정보가 없습니다." />

  return (
    <section className="page">
      <Link className="back-link" to="/concerts">
        ← 목록
      </Link>
      <div className="page-header">
        <h1>{item.title}</h1>
        <p className="lede">{item.place || item.institution || '장소 정보 없음'}</p>
      </div>

      <div className="panel">
        {item.image_url && (
          <img
            className="detail-image"
            src={item.image_url}
            alt={item.title}
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        )}
        <dl className="kv">
          <dt>기관</dt>
          <dd>{item.institution || '-'}</dd>
          <dt>종류</dt>
          <dd>{item.event_kind || '-'}</dd>
          <dt>분류</dt>
          <dd>{item.category || '-'}</dd>
          <dt>기간</dt>
          <dd>{item.period || '-'}</dd>
          <dt>장소</dt>
          <dd>{item.place || '-'}</dd>
          <dt>상세 링크</dt>
          <dd>
            {item.detail_url ? (
              <a href={item.detail_url} target="_blank" rel="noreferrer">
                원문 바로가기
              </a>
            ) : (
              '-'
            )}
          </dd>
        </dl>
        {item.summary && (
          <>
            <h2>소개</h2>
            <p className="intro-text pre-wrap">{item.summary}</p>
          </>
        )}
      </div>
    </section>
  )
}
