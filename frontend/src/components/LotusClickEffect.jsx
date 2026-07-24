import { useEffect, useRef } from 'react'

const PETAL_COLORS = ['#E8A0C0', '#F2B8CF', '#F7C9DB', '#D484A8', '#F6D5E4']

export default function LotusClickEffect() {
  const layerRef = useRef(null)

  useEffect(() => {
    function spawnPetals(clientX, clientY) {
      const layer = layerRef.current
      if (!layer) return

      for (let i = 0; i < 10; i += 1) {
        const petal = document.createElement('span')
        petal.className = 'lotus-petal'
        const angle = (Math.PI * 2 * i) / 10 + Math.random() * 0.4
        const dist = 40 + Math.random() * 70
        const dx = Math.cos(angle) * dist
        const dy = Math.sin(angle) * dist + 40 + Math.random() * 80
        const rot = -40 + Math.random() * 80
        petal.style.left = `${clientX}px`
        petal.style.top = `${clientY}px`
        petal.style.setProperty('--dx', `${dx}px`)
        petal.style.setProperty('--dy', `${dy}px`)
        petal.style.setProperty('--rot', `${rot}deg`)
        petal.style.background = PETAL_COLORS[i % PETAL_COLORS.length]
        petal.style.animationDelay = `${i * 18}ms`
        layer.appendChild(petal)
        petal.addEventListener('animationend', () => petal.remove())
      }
    }

    function onPointerDown(event) {
      if (event.button != null && event.button !== 0) return
      spawnPetals(event.clientX, event.clientY)
    }

    window.addEventListener('pointerdown', onPointerDown)
    return () => window.removeEventListener('pointerdown', onPointerDown)
  }, [])

  return <div ref={layerRef} className="lotus-petal-layer" aria-hidden="true" />
}
