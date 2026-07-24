import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getNearbyAttractions, getTemple } from '../api'
import { EmptyState, ErrorState, Loading } from '../components/Status'

const TABS = [
  { id: 'intro', label: '사찰소개' },
  { id: 'guide', label: '사찰안내' },
  { id: 'facility', label: '시설안내' },
  { id: 'gallery', label: '갤러리' },
  { id: 'reviews', label: '체험후기' },
]

export default function TempleDetailPage() {
  const { id } = useParams()
  const [temple, setTemple] = useState(null)
  const [nearby, setNearby] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState('intro')
  const [activeProgram, setActiveProgram] = useState(null)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [detail, nearbyData] = await Promise.all([
        getTemple(id),
        getNearbyAttractions(id),
      ])
      setTemple(detail)
      const programs = (detail.experience_programs || []).filter((p) => p.reservable)
      setActiveProgram(programs[0]?.id || null)
      setNearby(nearbyData.items || [])
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
  if (!temple) return <EmptyState message="템플스테이 정보가 없습니다." />

  const programs = (temple.experience_programs || []).filter((p) => p.reservable)
  const selected = programs.find((p) => p.id === activeProgram) || programs[0]

  return (
    <section className="page">
      <Link className="back-link" to="/temples">
        ← 목록
      </Link>
      <div className="page-header">
        <h1>{temple.name}</h1>
        <p className="lede">{temple.address || '주소 정보 없음'}</p>
        <div className="sns-row">
          {temple.youtube_url && (
            <a
              className="btn btn-secondary"
              href={temple.youtube_url}
              target="_blank"
              rel="noreferrer"
            >
              YouTube
            </a>
          )}
          {temple.instagram_url && (
            <a
              className="btn btn-secondary"
              href={temple.instagram_url}
              target="_blank"
              rel="noreferrer"
            >
              Instagram
            </a>
          )}
          {temple.homepage && (
            <a
              className="btn btn-secondary homepage-shortcut"
              href={temple.homepage}
              target="_blank"
              rel="noreferrer"
            >
              홈페이지·예약
            </a>
          )}
        </div>
      </div>

      {temple.image_url && (
        <img
          className="detail-image temple-hero-image"
          src={temple.image_url}
          alt={`${temple.name} 대표 이미지`}
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}

      {programs.length > 0 && (
        <div className="panel program-tabs-panel">
          <h2>예약 가능 체험 프로그램</h2>
          <p className="meta">작은 사진 탭을 누르면 일정·소개를 바로 볼 수 있습니다.</p>
          <div className="program-thumb-tabs" role="tablist" aria-label="체험 프로그램">
            {programs.map((prog) => (
              <button
                key={prog.id}
                type="button"
                role="tab"
                aria-selected={selected?.id === prog.id}
                className={selected?.id === prog.id ? 'program-thumb active' : 'program-thumb'}
                onClick={() => setActiveProgram(prog.id)}
              >
                <img src={prog.image_url} alt="" />
                <span>{prog.name}</span>
              </button>
            ))}
          </div>
          {selected && (
            <div className="program-thumb-detail">
              <h3>{selected.name}</h3>
              <p>{selected.summary}</p>
              {selected.dates?.length > 0 && (
                <p className="meta">
                  예약 가능일:{' '}
                  {selected.dates.slice(0, 8).join(', ')}
                  {selected.dates.length > 8 ? ' …' : ''}
                </p>
              )}
              {temple.homepage && (
                <a
                  className="btn"
                  href={temple.homepage}
                  target="_blank"
                  rel="noreferrer"
                >
                  예약하러 가기
                </a>
              )}
            </div>
          )}
        </div>
      )}

      <div className="detail-tabs" role="tablist" aria-label="사찰 정보">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            className={tab === item.id ? 'chip active' : 'chip'}
            aria-selected={tab === item.id}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="panel tab-panel">
        {tab === 'intro' && (
          <>
            <h2>사찰소개</h2>
            <p className="intro-text pre-wrap">
              {temple.intro_text || temple.description || '소개 정보가 준비 중입니다.'}
            </p>
            <dl className="kv stacked">
              <dt>음식</dt>
              <dd>{temple.food || '-'}</dd>
              <dt>주변 환경</dt>
              <dd>{temple.environment || '-'}</dd>
              <dt>특이점</dt>
              <dd>{temple.specialty || '-'}</dd>
              <dt>장점</dt>
              <dd>{temple.strengths || '-'}</dd>
            </dl>
          </>
        )}
        {tab === 'guide' && (
          <>
            <h2>사찰안내</h2>
            <p className="intro-text pre-wrap">
              {temple.guide_text || '안내 정보가 준비 중입니다.'}
            </p>
            <dl className="kv">
              <dt>연락처</dt>
              <dd>{temple.phone || '-'}</dd>
              <dt>지역</dt>
              <dd>{temple.region || '-'}</dd>
              <dt>산</dt>
              <dd>{temple.mountain || '-'}</dd>
              <dt>프로그램</dt>
              <dd>{temple.program || '-'}</dd>
            </dl>
          </>
        )}
        {tab === 'facility' && (
          <>
            <h2>시설안내</h2>
            <p className="intro-text pre-wrap">
              {temple.facility_text || '시설 정보가 준비 중입니다.'}
            </p>
          </>
        )}
        {tab === 'gallery' && (
          <>
            <h2>갤러리</h2>
            {(temple.gallery || []).length === 0 ? (
              <EmptyState message="갤러리 이미지가 없습니다." />
            ) : (
              <div className="gallery-grid">
                {temple.gallery.map((url) => (
                  <img key={url} src={url} alt={`${temple.name} 갤러리`} />
                ))}
              </div>
            )}
          </>
        )}
        {tab === 'reviews' && (
          <>
            <h2>체험후기</h2>
            {(temple.reviews || []).length === 0 ? (
              <EmptyState message="등록된 후기가 없습니다." />
            ) : (
              <ul className="review-list">
                {temple.reviews.map((review, idx) => (
                  <li key={`${review.author}-${idx}`}>
                    <strong>{review.author}</strong>
                    {review.rating != null && (
                      <span className="meta"> · ★{review.rating}</span>
                    )}
                    <p>{review.text}</p>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>

      <div className="panel">
        <h2>주변 관광 추천 (경기도)</h2>
        {nearby.length === 0 ? (
          <EmptyState message="주변에 매칭되는 관광 정보가 없습니다." />
        ) : (
          <ul className="card-list">
            {nearby.map((item) => (
              <li key={item.id} className="card-item">
                <Link to={`/attractions/${item.id}`}>
                  <h3>{item.name}</h3>
                  <p>{item.address || '위치 정보 없음'}</p>
                  <p className="meta">
                    {[item.category, item.distance_km != null ? `${item.distance_km}km` : null]
                      .filter(Boolean)
                      .join(' · ')}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
