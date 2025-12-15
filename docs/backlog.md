# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story’s `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2025-12-12 | 1.3 | 1    | Enhancement | Low      | TBD   | Open   | Make frontend verification URL configurable via environment variable in `backend/app/core/auth_service.py`. (file: backend/app/core/auth_service.py) |
| 2025-12-14 | 1.4 | 1 | Bug | High | TBD | Open | Implement full JWT validation in `backend/main.py`'s `get_current_user` function. (file: `backend/main.py`) |
| 2025-12-14 | 1.4 | 1 | Test | Medium | TBD | Open | Prioritize and implement E2E tests for the complete login flow. (file: `the-ai-helping-tool/cypress/e2e/login_flow.cy.tsx`) |
| 2025-12-14 | 1.4 | 1 | Test | Medium | TBD | Open | Clarify and implement a test case for unverified user login. (file: `backend/tests/test_auth_service.py` or `backend/tests/test_main.py`) |
| 2025-12-14 | 1.4 | 1 | Enhancement | Low | TBD | Open | Implement more comprehensive client-side input validation for password strength and email format in `LoginForm.tsx`. (file: `the-ai-helping-tool/components/auth/LoginForm.tsx`) |
| 2025-12-14 | 1.4 | 1 | Refactor | Low | TBD | Open | Replace `print` statements with structured logging using Python's `logging` module in `backend/app/core/auth_service.py`. (file: `backend/app/core/auth_service.py`) |
| 2025-12-14 | 1.4 | 1 | Security | Low | TBD | Open | Investigate and implement token storage using HttpOnly cookies instead of `localStorage` in `the-ai-helping-tool/services/authService.ts`. (file: `the-ai-helping-tool/services/authService.ts`) |
| 2025-12-15 | 1.4 | 1 | Security | Medium | TBD | Open | Implement robust storage and verification for email verification tokens (replace mock). (file: `backend/app/core/auth_service.py`) |
| 2025-12-15 | 1.4 | 1 | Refactor | Medium | TBD | Open | Use the actual `sub` from the JWT for `auth_provider_id` instead of a placeholder. (file: `backend/app/core/auth_service.py`) |
| 2025-12-15 | 1.4 | 1 | Docs | Medium | TBD | Open | Create the `tech-spec-epic-1.md` documentation. (file: `docs/tech-spec-epic-1.md`) |