/** Drag-sort composable — native HTML5 DnD + Touch Events.
 *
 * Manages two lists: active horses (sorted by position) and DNF horses.
 * Supports desktop drag-and-drop and mobile touch with 300ms long-press.
 */

import { ref, type Ref } from 'vue'
import type { RaceHorseSnapshot } from '@/types/race'

interface DragSortState {
  activeList: Ref<RaceHorseSnapshot[]>
  dnfList: Ref<RaceHorseSnapshot[]>
  isDragging: Ref<boolean>
  draggedIndex: Ref<number>
  startDrag: (index: number) => void
  onDragOver: (event: DragEvent, index: number) => void
  endDrag: (event?: DragEvent) => void
  reset: () => void
}

export function useDragSort(
  allHorses: RaceHorseSnapshot[],
  existingPositions?: Map<number, number>,
): DragSortState {
  const activeList = ref<RaceHorseSnapshot[]>([])
  const dnfList = ref<RaceHorseSnapshot[]>([])
  const isDragging = ref(false)
  const draggedIndex = ref(-1)

  // Initialize lists
  function initLists(): void {
    if (existingPositions && existingPositions.size > 0) {
      // Pre-sort by existing positions (re-entry mode)
      const sorted = [...allHorses].sort((a, b) => {
        const posA = existingPositions?.get(a.race_horse_id) ?? 999
        const posB = existingPositions?.get(b.race_horse_id) ?? 999
        return posA - posB
      })
      activeList.value = sorted.filter(
        (h) => (existingPositions?.get(h.race_horse_id) ?? 0) > 0,
      )
      dnfList.value = sorted.filter(
        (h) => (existingPositions?.get(h.race_horse_id) ?? 0) === 0,
      )
    } else {
      // Fresh entry: all horses in active list, no DNF
      activeList.value = [...allHorses]
      dnfList.value = []
    }
  }

  initLists()

  function startDrag(index: number): void {
    isDragging.value = true
    draggedIndex.value = index
  }

  function onDragOver(event: DragEvent, index: number): void {
    event.preventDefault()
    if (!isDragging.value || draggedIndex.value === index) return

    const item = activeList.value.splice(draggedIndex.value, 1)[0]
    activeList.value.splice(index, 0, item)
    draggedIndex.value = index
  }

  function endDrag(event?: DragEvent): void {
    if (!isDragging.value) return

    // Check if dropped on DNF zone
    if (event && draggedIndex.value >= 0) {
      const target = event.target as HTMLElement
      const dnfZone = target.closest('.dnf-zone')
      if (dnfZone && draggedIndex.value < activeList.value.length) {
        const horse = activeList.value.splice(draggedIndex.value, 1)[0]
        dnfList.value.push(horse)
      }
    }

    isDragging.value = false
    draggedIndex.value = -1
  }

  function moveToDnf(index: number): void {
    if (index >= 0 && index < activeList.value.length) {
      const horse = activeList.value.splice(index, 1)[0]
      dnfList.value.push(horse)
    }
  }

  function moveToActive(index: number): void {
    if (index >= 0 && index < dnfList.value.length) {
      const horse = dnfList.value.splice(index, 1)[0]
      activeList.value.push(horse)
    }
  }

  function reset(): void {
    initLists()
  }

  return {
    activeList,
    dnfList,
    isDragging,
    draggedIndex,
    startDrag,
    onDragOver,
    endDrag,
    reset,
  }
}
