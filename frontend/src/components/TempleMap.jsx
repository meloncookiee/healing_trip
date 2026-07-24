import { useEffect, useRef } from 'react'
import PlacesMap from './PlacesMap'

export default function TempleMap({ temples = [] }) {
  const linkFor = useRef((item) => `/temples/${item.id}`).current
  return (
    <PlacesMap
      places={temples}
      title="지도에서 한눈에"
      listPath="/temples"
      label="사찰"
      linkFor={linkFor}
    />
  )
}
