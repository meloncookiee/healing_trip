import { useEffect, useState } from 'react'
import { addFavorite, checkFavorite, removeFavorite } from '../api'

export default function FavoriteButton({ itemType, itemId }) {
  const [favorited, setFavorited] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    checkFavorite(itemType, itemId)
      .then((data) => {
        if (alive) setFavorited(Boolean(data.favorited))
      })
      .catch(() => {
        if (alive) setFavorited(false)
      })
    return () => {
      alive = false
    }
  }, [itemType, itemId])

  async function toggle() {
    setBusy(true)
    try {
      if (favorited) {
        await removeFavorite(itemType, itemId)
        setFavorited(false)
      } else {
        await addFavorite(itemType, itemId)
        setFavorited(true)
      }
    } catch (err) {
      alert(err.message || '즐겨찾기 처리에 실패했습니다.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <button
      type="button"
      className={favorited ? 'btn btn-fav active' : 'btn btn-fav'}
      onClick={toggle}
      disabled={busy || !itemId}
    >
      {favorited ? '★ 저장됨' : '☆ 저장'}
    </button>
  )
}
