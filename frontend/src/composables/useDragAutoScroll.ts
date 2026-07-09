/**
 * Auto-scroll composable for drag-and-drop scenarios.
 * Smoothly scrolls the page when the pointer is near the top/bottom 1/5 of the viewport.
 *
 * Desktop: uses a document-level dragover listener with preventDefault to eliminate
 * "not-allowed" cursor at edges and capture clientY anywhere in the viewport.
 * Mobile: clientY is fed from the parent component's touchmove handlers.
 */

import { ref, watch, onUnmounted, type Ref } from 'vue'

const EDGE_RATIO = 0.2
const BASE_SPEED = 8
const MAX_SPEED = 20

function onDocumentDragOver(this: { clientY: Ref<number> }, event: DragEvent) {
  event.preventDefault()
  this.clientY.value = event.clientY
}

export function useDragAutoScroll(options: {
  enabled: Ref<boolean>
  clientY: Ref<number>
}): {
  autoScrollDirection: Ref<'up' | 'down' | null>
} {
  const autoScrollDirection = ref<'up' | 'down' | null>(null)
  let rafId: number | null = null
  let docDragOverBound: ((e: DragEvent) => void) | null = null

  function getScrollContainer(): HTMLElement | Window {
    const el = document.querySelector('.scroll-container')
    if (el) {
      const style = window.getComputedStyle(el)
      if (
        style.overflowY === 'auto' ||
        style.overflowY === 'scroll' ||
        style.overflow === 'auto' ||
        style.overflow === 'scroll'
      ) {
        return el as HTMLElement
      }
    }
    const se = document.scrollingElement
    if (se && se.scrollHeight > se.clientHeight) {
      return se as HTMLElement
    }
    return window
  }

  function isScrolledToTop(container: HTMLElement | Window): boolean {
    if (container instanceof Window) {
      return window.scrollY <= 0
    }
    return container.scrollTop <= 0
  }

  function isScrolledToBottom(container: HTMLElement | Window): boolean {
    if (container instanceof Window) {
      return window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 1
    }
    return container.scrollTop + container.clientHeight >= container.scrollHeight - 1
  }

  function scroll(): void {
    if (!options.enabled.value) {
      autoScrollDirection.value = null
      return
    }

    const y = options.clientY.value
    if (y <= 0) {
      autoScrollDirection.value = null
      rafId = requestAnimationFrame(scroll)
      return
    }

    const vh = window.innerHeight
    const threshold = vh * EDGE_RATIO

    if (y < threshold) {
      autoScrollDirection.value = 'up'
      const distanceRatio = (threshold - y) / threshold
      const speed = Math.min(BASE_SPEED * distanceRatio * distanceRatio, MAX_SPEED)

      const container = getScrollContainer()
      if (!isScrolledToTop(container)) {
        if (container instanceof Window) {
          window.scrollBy(0, -speed)
        } else {
          container.scrollBy(0, -speed)
        }
      }
    } else if (y > vh - threshold) {
      autoScrollDirection.value = 'down'
      const distanceFromBottom = y - (vh - threshold)
      const distanceRatio = distanceFromBottom / threshold
      const speed = Math.min(BASE_SPEED * distanceRatio * distanceRatio, MAX_SPEED)

      const container = getScrollContainer()
      if (!isScrolledToBottom(container)) {
        if (container instanceof Window) {
          window.scrollBy(0, speed)
        } else {
          container.scrollBy(0, speed)
        }
      }
    } else {
      autoScrollDirection.value = null
    }

    rafId = requestAnimationFrame(scroll)
  }

  function start(): void {
    if (rafId !== null) return
    // Bind document-level dragover so auto-scroll works at viewport edges
    // regardless of whether the mouse is over a drop-target element
    docDragOverBound = onDocumentDragOver.bind({ clientY: options.clientY })
    document.addEventListener('dragover', docDragOverBound)
    rafId = requestAnimationFrame(scroll)
  }

  function stop(): void {
    if (rafId !== null) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    if (docDragOverBound) {
      document.removeEventListener('dragover', docDragOverBound)
      docDragOverBound = null
    }
    autoScrollDirection.value = null
  }

  watch(
    () => options.enabled.value,
    (val) => {
      if (val) {
        start()
      } else {
        stop()
      }
    },
  )

  onUnmounted(() => {
    stop()
  })

  return { autoScrollDirection }
}
