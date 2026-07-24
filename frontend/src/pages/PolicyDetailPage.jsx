import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getPolicy } from '../api'
import { DdayBadge } from '../components/DdayBadge'
import FavoriteButton from '../components/FavoriteButton'
import { ErrorState, Loading } from '../components/Status'

export default function PolicyDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    getPolicy(id)
      .then(setItem)
      .catch((err) => setError(err.message || '상세를 불러오지 못했습니다.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />
  if (!item) return null

  return (
    <div className="page">
      <Link className="back-link" to="/policies">
        ← 목록으로
      </Link>
      <div className="card-top detail-title">
        <h1 className="page-title">{item.title}</h1>
        <DdayBadge item={item} />
      </div>
      <p className="page-desc">
        {item.organization || '기관미상'} · {item.region || '전국'} · {item.category || '분야미상'}
      </p>
      <div className="toolbar">
        <FavoriteButton itemType="policy" itemId={item.id} />
      </div>

      <div className="detail-grid">
        <DetailBlock label="신청기간" value={item.apply_period || item.apply_end || '-'} />
        <DetailBlock label="지원대상" value={item.target || '-'} />
        <DetailBlock label="지원내용" value={item.support_content || '-'} />
        <DetailBlock label="신청방법" value={item.apply_method || '-'} />
        <DetailBlock label="정책설명" value={item.description || '-'} />
      </div>

      {item.official_url && (
        <a className="btn btn-primary" href={item.official_url} target="_blank" rel="noreferrer">
          공식 페이지 열기
        </a>
      )}
    </div>
  )
}

function DetailBlock({ label, value }) {
  return (
    <section className="panel detail-block">
      <h2>{label}</h2>
      <p>{value}</p>
    </section>
  )
}
