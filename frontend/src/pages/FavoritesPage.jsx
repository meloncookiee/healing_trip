import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getFavorites, removeFavorite } from '../api'
import { DdayBadge } from '../components/DdayBadge'
import { EmptyState, ErrorState, Loading } from '../components/Status'

const TABS = [
  { key: '', label: '전체' },
  { key: 'policy', label: '정책' },
  { key: 'job', label: '채용' },
  { key: 'space', label: '공간' },
]

export default function FavoritesPage() {
  const [tab, setTab] = useState('')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load(nextTab = tab) {
    setLoading(true)
    setError('')
    try {
      const data = await getFavorites({ itemType: nextTab || undefined })
      setItems(data.items || [])
    } catch (err) {
      setError(err.message || '즐겨찾기를 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load('')
  }, [])

  function handleTab(next) {
    setTab(next)
    load(next)
  }

  async function handleRemove(fav) {
    try {
      await removeFavorite(fav.item_type, fav.item_id)
      await load(tab)
    } catch (err) {
      alert(err.message || '삭제 실패')
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">즐겨찾기</h1>
      <p className="page-desc">저장한 정책·채용·공간을 한곳에서 관리합니다.</p>

      <div className="chip-row">
        {TABS.map((t) => (
          <button
            key={t.key || 'all'}
            type="button"
            className={tab === t.key ? 'chip active' : 'chip'}
            onClick={() => handleTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <Loading />}
      {!loading && error && <ErrorState message={error} onRetry={() => load(tab)} />}
      {!loading && !error && items.length === 0 && (
        <EmptyState message="저장한 항목이 없습니다. 상세 화면에서 ☆ 저장을 눌러 보세요." />
      )}
      {!loading && !error && items.length > 0 && (
        <ul className="card-list">
          {items.map((fav) => (
            <li key={fav.id} className="card-item static-card">
              <div className="card-top">
                <strong>
                  [{labelType(fav.item_type)}] {titleOf(fav)}
                </strong>
                {fav.item && (fav.item_type === 'policy' || fav.item_type === 'job') && (
                  <DdayBadge item={fav.item} />
                )}
              </div>
              <span className="meta">{metaOf(fav)}</span>
              <div className="row-actions">
                {linkOf(fav) && (
                  <Link className="btn btn-secondary" to={linkOf(fav)}>
                    상세
                  </Link>
                )}
                <button
                  type="button"
                  className="btn btn-fav"
                  onClick={() => handleRemove(fav)}
                >
                  삭제
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function labelType(type) {
  return { policy: '정책', job: '채용', space: '공간' }[type] || type
}

function titleOf(fav) {
  const item = fav.item
  if (!item) return `#${fav.item_id}`
  return item.title || item.name || `#${fav.item_id}`
}

function metaOf(fav) {
  const item = fav.item
  if (!item) return '원본이 삭제되었거나 없습니다.'
  if (fav.item_type === 'job') {
    return `${item.company || ''} · ${item.region || ''}`
  }
  if (fav.item_type === 'policy') {
    return `${item.organization || ''} · ${item.region || '전국'}`
  }
  return `${item.region || ''} · ${item.address || ''}`
}

function linkOf(fav) {
  if (fav.item_type === 'policy') return `/policies/${fav.item_id}`
  if (fav.item_type === 'job') return `/jobs/${fav.item_id}`
  return null
}
