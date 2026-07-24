import { useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'

/**
 * places: [{ id, name, address?, lat, lng }]
 * linkFor: (place) => path string
 */
export default function PlacesMap({
  places = [],
  title = '지도에서 한눈에',
  listPath = '/',
  linkFor,
  label = '장소',
}) {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)
  const layerRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    const L = window.L
    if (!L || !mapRef.current) return

    if (!mapInstance.current) {
      mapInstance.current = L.map(mapRef.current, {
        scrollWheelZoom: false,
      }).setView([37.4138, 127.5183], 9)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 18,
      }).addTo(mapInstance.current)

      layerRef.current = L.layerGroup().addTo(mapInstance.current)
    }

    const map = mapInstance.current
    const layer = layerRef.current
    layer.clearLayers()

    const points = places.filter(
      (item) => item.lat != null && item.lng != null && !Number.isNaN(item.lat) && !Number.isNaN(item.lng),
    )

    const bounds = []
    points.forEach((item) => {
      const marker = L.marker([item.lat, item.lng])
      const path = linkFor ? linkFor(item) : '#'
      marker.bindPopup(
        `<strong>${item.name}</strong><br/><span>${item.address || item.region || ''}</span><br/><button type="button" data-place-id="${item.id}" class="map-popup-link">상세 보기</button>`,
      )
      marker.on('popupopen', () => {
        const btn = document.querySelector(`.map-popup-link[data-place-id="${item.id}"]`)
        if (!btn) return
        btn.onclick = () => navigate(path)
      })
      marker.addTo(layer)
      bounds.push([item.lat, item.lng])
    })

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [28, 28] })
    } else if (bounds.length === 1) {
      map.setView(bounds[0], 12)
    } else {
      map.setView([37.4138, 127.5183], 9)
    }

    setTimeout(() => map.invalidateSize(), 80)
  }, [places, navigate, linkFor])

  useEffect(() => {
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [])

  const withCoords = places.filter((t) => t.lat != null && t.lng != null).length

  return (
    <div className="temple-map-panel">
      <div className="temple-map-head">
        <h2>{title}</h2>
        <p className="meta">
          좌표 있는 {label} {withCoords}곳 표시
        </p>
      </div>
      <div ref={mapRef} className="temple-map" />
      {withCoords === 0 && (
        <p className="meta map-empty">표시할 좌표가 없습니다.</p>
      )}
      <p className="meta map-tip">
        마커를 누르면 상세로 이동할 수 있습니다. · <Link to={listPath}>목록으로</Link>
      </p>
    </div>
  )
}
