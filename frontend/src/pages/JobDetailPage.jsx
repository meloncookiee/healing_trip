import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getJob } from '../api'
import { DdayBadge } from '../components/DdayBadge'
import FavoriteButton from '../components/FavoriteButton'
import { ErrorState, Loading } from '../components/Status'

export default function JobDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    getJob(id)
      .then(setItem)
      .catch((err) => setError(err.message || '상세를 불러오지 못했습니다.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />
  if (!item) return null

  return (
    <div className="page">
      <Link className="back-link" to="/jobs">
        ← 목록으로
      </Link>
      <div className="card-top detail-title">
        <h1 className="page-title">{item.title}</h1>
        <DdayBadge item={item} />
      </div>
      <p className="page-desc">
        {item.company} · {item.region || '지역미상'} · {item.job_field || '직무미상'}
      </p>
      <div className="toolbar">
        <FavoriteButton itemType="job" itemId={item.id} />
      </div>

      <div className="detail-grid">
        <section className="panel detail-block">
          <h2>기본 정보</h2>
          <p>고용형태: {item.employment_type || '-'}</p>
          <p>경력: {item.career || '-'}</p>
          <p>마감일: {item.deadline || '-'}</p>
        </section>
        <section className="panel detail-block">
          <h2>상세</h2>
          <p className="pre-wrap">{item.description || '상세 내용이 없습니다.'}</p>
        </section>
      </div>

      {item.official_url && (
        <a className="btn btn-primary" href={item.official_url} target="_blank" rel="noreferrer">
          원문 공고 열기
        </a>
      )}
    </div>
  )
}
