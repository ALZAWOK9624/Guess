# Edge Case Hunter — Review Prompt

You have read access to the project at `d:/horses/wp10data/vibe_project/guess`. Review the following changes for edge cases, boundary conditions, error states, and untested paths.

## Changes to Review

### 1. New files (read the actual files):
- `frontend/src/components/ConfirmDeleteModal.vue`
- `frontend/src/components/GradeBadge.vue`
- `frontend/src/components/StatusBadge.vue`
- `frontend/src/pages/admin/DashboardPage.vue` (rewritten)

### 2. Modified files (read full current state):
- `frontend/src/pages/admin/EditRacePage.vue`
- `backend/tests/test_races.py`

### 3. Context:
- The backend `DELETE /api/v1/races/{id}` endpoint already existed (Story 2.3). Only tests were added.
- The story is `_bmad-output/implementation-artifacts/2-4-race-deletion-horse-details.md`
- Race model has `cascade="all, delete-orphan"` for race_horses relationship

### 4. Check for:
- What happens when delete is called and network fails mid-request?
- What if the race has votes (Vote model doesn't exist yet, but will in future)?
- Race name with special characters in delete confirmation modal
- Concurrent delete requests (double-click on delete button)
- Empty race list after all races deleted
- What if `raceToDelete` becomes null/undefined mid-deletion?
- Horse name that contains `{name}` literal string in the modal
- Age field can be null — does `toLowerCase()` on grade handle null/undefined?
- The modal's `@click.self` does nothing (missing handler)
- `aria-labelledby` points to `titleId` but that ID is not defined in the template
- The confirm button in ConfirmDeleteModal doesn't prevent double-click race condition beyond the disabled prop
- DashboardPage loads races on mount — what if the component is unmounted before load completes?
- EditRacePage's non-editable state (settled) now shows no delete button — correct per spec
- But what about the locked state? Locked races CAN be deleted but the edit page form is disabled for editing. The delete button should still show.

Report findings as a Markdown list: severity (High/Med/Low), category (EdgeCase/MissingEdgeCase/ErrorPath/DataRace/Boundary), description with line references, suggested fix.
