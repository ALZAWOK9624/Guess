/** Drag-sort composable — native HTML5 DnD + Touch Events.
 *
 * Manages two lists: active horses (sorted by position) and DNF horses.
 * Reordering happens on drop (not during dragover) to avoid DOM mutation mid-drag.
 */

import { ref, type Ref } from 'vue'
import type { RaceHorseSnapshot } from '@/types/race'

type DragMode = 'result' | 'gate'

interface DragSortOptions {
  mode?: DragMode
}

interface DragSortState {
  activeList: Ref<RaceHorseSnapshot[]>
  dnfList: Ref<RaceHorseSnapshot[]>
  isDragging: Ref<boolean>
  draggedIndex: Ref<number>
  startDrag: (index: number) => void
  commitReorder: (fromIndex: number, toIndex: number) => void
  moveToDnf: (index: number) => void
  moveToActive: (index: number) => void
  endDrag: () => void
  reset: () => void
}

export function useDragSort(
  allHorses: RaceHorseSnapshot[],
  existingPositions?: Map<number, number>,
  options: DragSortOptions = {},
): DragSortState {
  const mode = options.mode || 'result'
  const activeList = ref<RaceHorseSnapshot[]>([])
  const dnfList = ref<RaceHorseSnapshot[]>([])
  const isDragging = ref(false)
  const draggedIndex = ref(-1)

  // Initialize lists
  function initLists(): void {
    if (mode === 'gate') {
      // Gate mode: single list sorted by gate, no DNF
      activeList.value = [...allHorses].sort((a, b) => {
        const gateA = a.gate ?? 999
        const gateB = b.gate ?? 999
        return gateA - gateB
      })
      dnfList.value = []
      return
    }

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

  function commitReorder(fromIndex: number, toIndex: number): void {
    if (fromIndex < 0 || fromIndex >= activeList.value.length) return
    if (toIndex < 0 || toIndex >= activeList.value.length) return
    if (fromIndex === toIndex) return
    const item = activeList.value.splice(fromIndex, 1)[0]
    activeList.value.splice(toIndex, 0, item)
  }

  function moveToDnf(index: number): void {
    if (mode === 'gate') return
    if (index >= 0 && index < activeList.value.length) {
      const horse = activeList.value.splice(index, 1)[0]
      dnfList.value.push(horse)
    }
  }

  function moveToActive(index: number): void {
    if (mode === 'gate') return
    if (index >= 0 && index < dnfList.value.length) {
      const horse = dnfList.value.splice(index, 1)[0]
      activeList.value.push(horse)
    }
  }

  function endDrag(): void {
    isDragging.value = false
    draggedIndex.value = -1
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
    commitReorder,
    moveToDnf,
    moveToActive,
    endDrag,
    reset,
  }
}
