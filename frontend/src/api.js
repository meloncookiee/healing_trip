// ---------------------------------------------------------------
// 백엔드(FastAPI) 호출 함수 모음
// 화면은 여기 함수만 부른다. 공공데이터 API는 직접 호출하지 않는다.
// ---------------------------------------------------------------
const BASE_URL = 'http://127.0.0.1:8001'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    let detail = '요청 실패'
    try {
      const body = await res.json()
      detail = body.detail || body.message || detail
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  if (res.status === 204) return null
  return res.json()
}

export async function checkHealth() {
  return request('/health')
}

export async function syncTemples() {
  return request('/temples/sync', { method: 'POST' })
}

export async function syncAttractions() {
  return request('/attractions/sync', { method: 'POST' })
}

export async function getTemples({ q, region, date, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (region) params.set('region', region)
  if (date) params.set('date', date)
  params.set('limit', String(limit))
  params.set('offset', String(offset))
  return request(`/temples?${params}`)
}

export async function getTempleRegions() {
  return request('/temples/regions')
}

export async function getTemple(id) {
  return request(`/temples/${id}`)
}

export async function getNearbyAttractions(templeId, { radiusKm = 20, limit = 20 } = {}) {
  const params = new URLSearchParams({
    radius_km: String(radiusKm),
    limit: String(limit),
  })
  return request(`/temples/${templeId}/nearby?${params}`)
}

export async function getAttractions({ q, category, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (category) params.set('category', category)
  params.set('limit', String(limit))
  params.set('offset', String(offset))
  return request(`/attractions?${params}`)
}

export async function getAttraction(id) {
  return request(`/attractions/${id}`)
}

export async function searchAll(q, limit = 50) {
  const params = new URLSearchParams({ q, limit: String(limit) })
  return request(`/search?${params}`)
}

export async function syncConcerts() {
  return request('/concerts/sync', { method: 'POST' })
}

export async function getConcerts({ q, category, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (category) params.set('category', category)
  params.set('limit', String(limit))
  params.set('offset', String(offset))
  return request(`/concerts?${params}`)
}

export async function getConcert(id) {
  return request(`/concerts/${id}`)
}
