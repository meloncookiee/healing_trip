export function formatDday(item) {
  if (!item || item.d_day == null) return null
  if (item.is_closed || item.d_day < 0) return '마감'
  if (item.d_day === 0) return 'D-Day'
  if (item.is_imminent) return `마감임박 D-${item.d_day}`
  return `D-${item.d_day}`
}

export function DdayBadge({ item }) {
  const label = formatDday(item)
  if (!label) return null
  const className = [
    'dday-badge',
    item.is_closed || item.d_day < 0 ? 'closed' : '',
    item.is_imminent && !(item.is_closed || item.d_day < 0) ? 'imminent' : '',
  ]
    .filter(Boolean)
    .join(' ')
  return <span className={className}>{label}</span>
}

export const REGIONS = [
  '서울',
  '경기',
  '부산',
  '대구',
  '인천',
  '광주',
  '대전',
  '울산',
  '세종',
  '강원',
  '충북',
  '충남',
  '전북',
  '전남',
  '경북',
  '경남',
  '제주',
]
