# Acceptance Auditor — Review Prompt

You are an Acceptance Auditor. Review the diff and new file content against the spec document.

## Spec: Story 2.4

`_bmad-output/implementation-artifacts/2-4-race-deletion-horse-details.md`

### Acceptance Criteria Summary:

**AC-1: Admin race list with delete**
- Dashboard at `/admin` shows all races with name/GradeBadge/StatusBadge/date/horse_count
- Action columns: edit → `/admin/races/:id/edit`, delete (hidden for settled)
- Delete confirmation modal: "确定删除「{race_name}」？所有投票记录将被清除。"
- Confirm calls DELETE API, removes from list
- Cancel closes modal without action
- Error on delete failure

**AC-2: Edit page delete button**
- voting/locked races: show delete button (destructive style)
- settled races: no delete button
- Delete confirmation same as AC-1
- After confirm: delete + redirect to /admin

**AC-3: HorseDetailCard verification**
- name as title, 9 attributes displayed, null shows `-`
- withDefaults + safeData for null protection

**AC-4: Backend API**
- DELETE settled → 400 (RACE_SETTLED)
- DELETE voting/locked → 204
- DELETE non-existent → 404

## Changes (diff + new files)

Review the following files against each AC:

1. `frontend/src/pages/admin/DashboardPage.vue` (full rewrite)
2. `frontend/src/pages/admin/EditRacePage.vue` (modified)
3. `frontend/src/components/ConfirmDeleteModal.vue` (new)
4. `frontend/src/components/GradeBadge.vue` (new)
5. `frontend/src/components/StatusBadge.vue` (new)
6. `backend/tests/test_races.py` (modified)

## Read the actual files from:
`d:/horses/wp10data/vibe_project/guess/`

Check for:
- Violations of acceptance criteria
- Deviations from spec intent
- Missing implementation of specified behavior
- Contradictions between spec constraints and actual code

Output findings as a Markdown list. Each finding: one-line title, which AC/constraint it violates, and evidence from the diff/code.
