import { useEffect, useRef, useState } from 'react'
import { getPublicConfig, getSpaces, getSpacesForMap, seedDemoSpaces } from '../api'
import FavoriteButton from '../components/FavoriteButton'
import { EmptyState, ErrorState, Loading } from '../components/Status'

function loadKakaoSdk(appKey) {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      window.kakao.maps.load(() => resolve(window.kakao))
      return
    }
    const existing = document.getElementById('kakao-map-sdk')
    if (existing) {
      existing.addEventListener('load', () => {
        window.kakao.maps.load(() => resolve(window.kakao))
      })
      return
    }
    const script = document.createElement('script')
    script.id = 'kakao-map-sdk'
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${appKey}&autoload=false`
    script.async = true
    script.onload = () => {
      if (!window.kakao?.maps) {
        reject(new Error('카카오맵 SDK 로드 실패'))
        return
      }
      window.kakao.maps.load(() => resolve(window.kakao))
    }
    script.onerror = () => reject(new Error('카카오맵 스크립트를 불러오지 못했습니다.'))
    document.head.appendChild(script)
  })
}

export default function SpacesPage() {
  const mapRef = useRef(null)
  const [items, setItems] = useState([])
  const [mapItems, setMapItems] = useState([])
  const [skipped, setSkipped] = useState(0)
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [mapMessage, setMapMessage] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [listData, mapData] = await Promise.all([getSpaces(), getSpacesForMap()])
      setItems(listData.items || [])
      setMapItems(mapData.items || [])
      setSkipped(mapData.skipped_no_coords || 0)
    } catch (err) {
      setError(err.message || '청년 공간을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    let cancelled = false

    async function drawMap() {
      if (!mapItems.length) {
        setMapMessage('좌표가 있는 공간이 없습니다. 샘플 데이터를 추가해 보세요.')
        return
      }
      try {
        const config = await getPublicConfig()
        const key = config.kakao_js_key
        if (!key) {
          setMapMessage(
            'KAKAO_JS_KEY가 없습니다. backend/.env에 카카오 JavaScript 키를 넣고 서버를 재시작하세요. 목록·좌표 데이터는 아래에 표시됩니다.',
          )
          return
        }
        const kakao = await loadKakaoSdk(key)
        if (cancelled || !mapRef.current) return

        const first = mapItems[0]
        const center = new kakao.maps.LatLng(first.latitude, first.longitude)
        const map = new kakao.maps.Map(mapRef.current, { center, level: 9 })
        const bounds = new kakao.maps.LatLngBounds()

        mapItems.forEach((space) => {
          const position = new kakao.maps.LatLng(space.latitude, space.longitude)
          bounds.extend(position)
          const marker = new kakao.maps.Marker({ map, position, title: space.name })
          kakao.maps.event.addListener(marker, 'click', () => {
            setSelectedId(space.id)
          })
        })
        map.setBounds(bounds)
        setMapMessage('')
      } catch (err) {
        setMapMessage(err.message || '지도를 표시하지 못했습니다.')
      }
    }

    drawMap()
    return () => {
      cancelled = true
    }
  }, [mapItems])

  async function handleSeed() {
    try {
      await seedDemoSpaces()
      await load()
    } catch (err) {
      alert(err.message || '샘플 추가 실패')
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">청년 공간</h1>
      <p className="page-desc">리스트와 지도(카카오맵)로 위치를 확인할 수 있습니다.</p>

      <div className="toolbar">
        <button type="button" className="btn btn-secondary" onClick={handleSeed}>
          샘플 공간 추가
        </button>
      </div>

      {loading && <Loading />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && (
        <>
          <section className="map-panel">
            <div className="map-canvas" ref={mapRef} />
            {mapMessage && <p className="map-note">{mapMessage}</p>}
            {skipped > 0 && (
              <p className="map-note">좌표 없는 항목 {skipped}건은 지도에서 제외했습니다.</p>
            )}
            {mapItems.length > 0 && !mapMessage.includes('KAKAO') && (
              <ul className="map-coord-list">
                {mapItems.map((s) => (
                  <li key={s.id}>
                    <button
                      type="button"
                      className={selectedId === s.id ? 'text-btn active' : 'text-btn'}
                      onClick={() => setSelectedId(s.id)}
                    >
                      {s.name} ({s.latitude?.toFixed(3)}, {s.longitude?.toFixed(3)})
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {items.length === 0 ? (
            <EmptyState message="공간 데이터가 없습니다. 샘플 추가 또는 /spaces/sync 를 실행하세요." />
          ) : (
            <ul className="card-list">
              {items.map((space) => (
                <li
                  key={space.id}
                  className={
                    selectedId === space.id ? 'card-item static-card selected' : 'card-item static-card'
                  }
                >
                  <div className="card-top">
                    <strong>{space.name}</strong>
                    <FavoriteButton itemType="space" itemId={space.id} />
                  </div>
                  <span className="meta">{space.region || '지역미상'}</span>
                  <span className="meta">{space.address || '주소 없음'}</span>
                  {space.phone && <span className="meta">☎ {space.phone}</span>}
                  {space.programs && <span className="meta">{space.programs}</span>}
                  <span className="meta">
                    {space.has_coords ? '좌표 있음' : '좌표 없음 (지도 제외)'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  )
}
