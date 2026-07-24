import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPreferences, savePreferences } from '../api'
import { ErrorState, Loading } from '../components/Status'

const REGIONS = [
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

const STATUSES = ['학생', '취준생', '재직자', '이직준비', '창업준비']
const INTERESTS = ['개발', '디자인', '마케팅', '보건', '교육', '금융', '공공', '창업']

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    region: '',
    age: '',
    status: '',
    interest: '',
  })

  useEffect(() => {
    getPreferences()
      .then((data) => {
        setForm({
          region: data.region || '',
          age: data.age ?? '',
          status: data.status || '',
          interest: data.interest || '',
        })
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await savePreferences({
        user_key: 'default',
        region: form.region,
        age: form.age === '' ? null : Number(form.age),
        status: form.status,
        interest: form.interest,
      })
      navigate('/')
    } catch (err) {
      setError(err.message || '저장에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading label="설정 불러오는 중…" />

  return (
    <div className="page page-narrow">
      <h1 className="page-title">맞춤 설정</h1>
      <p className="page-desc">지역·연령·상태·관심 분야를 입력하면 홈에서 맞춤 정보를 보여 줍니다.</p>

      {error && <ErrorState message={error} />}

      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>거주 지역 (시/도)</span>
          <select
            value={form.region}
            onChange={(e) => update('region', e.target.value)}
            required
          >
            <option value="">선택</option>
            {REGIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>연령</span>
          <input
            type="number"
            min="15"
            max="45"
            value={form.age}
            onChange={(e) => update('age', e.target.value)}
            placeholder="예: 28"
            required
          />
        </label>

        <label className="field">
          <span>현재 상태</span>
          <select
            value={form.status}
            onChange={(e) => update('status', e.target.value)}
            required
          >
            <option value="">선택</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>관심 분야</span>
          <select
            value={form.interest}
            onChange={(e) => update('interest', e.target.value)}
            required
          >
            <option value="">선택</option>
            {INTERESTS.map((i) => (
              <option key={i} value={i}>
                {i}
              </option>
            ))}
          </select>
        </label>

        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? '저장 중…' : '저장하고 홈으로'}
        </button>
      </form>
    </div>
  )
}
