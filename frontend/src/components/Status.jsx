export function Loading({ label = '불러오는 중…' }) {
  return <div className="state state-loading">{label}</div>
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state state-error">
      <p>{message || '오류가 발생했습니다.'}</p>
      {onRetry && (
        <button type="button" className="btn btn-secondary" onClick={onRetry}>
          다시 시도
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message = '표시할 내용이 없습니다.' }) {
  return <div className="state state-empty">{message}</div>
}
