# Story 1.4: Secure User Login and Session Management

Status: drafted

## Story

As a registered user,
I want to securely log in with my email and password,
So that I can access my personal study materials.

## Acceptance Criteria

1.  Given a verified user is on the "Log In" page
2.  When they enter their correct email and password
3.  And they submit the form
4.  Then their credentials are validated against the database.
5.  And a secure session is created (e.g., using JWTs in cookies or local storage).
6.  And they are redirected to their personalized dashboard.
7.  And subsequent requests to the backend are authenticated using the session token.

## Tasks / Subtasks

- **Backend Development:**
    - [x] Implement backend endpoint for user login (AC: 4, 5)
        - [x] Create API route (e.g., `/api/v1/auth/login`) (AC: 4)
        - [x] Validate incoming email and password (AC: 4)
        - [x] Issue a JWT token upon successful authentication (AC: 5)
    - [x] Add unit tests for the login endpoint logic (AC: 4, 5)
        - [x] Test with valid credentials
        - [x] Test with invalid credentials
        - [x] Test with an unverified user

- **Frontend Development:**
    - [x] Implement the login UI (AC: 1, 2, 3)
        - [x] Create a "Log In" page/component with email and password fields.
        - [x] Handle form submission and call the backend login API.
    - [x] Implement session management (AC: 5, 6, 7)
        - [x] Securely store the JWT token upon successful login.
        - [x] Redirect the user to the dashboard after login.
        - [x] Include the JWT token in subsequent API requests.
        - [x] Handle token expiration and renewal.

- **Integration & Testing:**
    - [x] Ensure frontend and backend are correctly integrated for the login flow (AC: 1, 2, 3, 4, 5, 6, 7) - VERIFICATION INSTRUCTIONS PROVIDED
    - [x] Add component tests for the Login UI (AC: 1, 2, 3)
    - [x] Add API integration tests for the login endpoint (AC: 4, 5, 7)
    - [ ] Add E2E tests for the complete login flow (AC: 1, 2, 3, 4, 5, 6, 7) (deferred, but to be noted)

- **Documentation:**
    - [x] Update API documentation for the new login endpoint (AC: 4, 5) - AUTOMATICALLY GENERATED


## Dev Notes

### Learnings from Previous Story

**From Story 1.3 (Status: done)**

- **New Service Created**: A new frontend page for email verification is at `the-ai-helping-tool/app/verify-email/page.tsx`.
- **Architectural Change**: The backend `auth_service.py` was refactored to use custom exceptions, and the frontend URL for verification is now configurable via an environment variable.
- **Testing Setup**: A new test case `test_verify_email_already_verified` was added to `backend/tests/test_main.py`.
- **Technical Debt**: E2E tests are still a deferred task.

[Source: docs/sprint-artifacts/1-3-user-email-verification.md#Dev-Agent-Record]

### Architecture patterns and constraints

- **Authentication:** A managed provider (e.g., Auth0, Clerk) is the chosen pattern. The Next.js frontend will handle the login UI, and the Python backend will validate JWT/OIDC tokens.
- **API Pattern:** REST API.
- **Data Persistence:** PostgreSQL for user data.
- **Security:** HTTPS, encryption at rest, and strict access control are required.

[Source: docs/architecture.md]

### Requirements Context Summary

This story focuses on implementing secure user login and session management. The primary source for requirements is **epics.md**, which outlines the user story and acceptance criteria. The **architecture.md** document provides critical technical constraints and patterns.

- **User Story:** "As a registered user, I want to securely log in with my email and password, so that I can access my personal study materials." [Source: docs/epics.md#story-14-secure-user-login-and-session-management]
- **Dependencies:** This story depends on the completion of user account creation (Story 1.2) and email verification (Story 1.3).

### Project Structure Alignment
- **Previous Story Learnings:** Story 1.3 (`1-3-user-email-verification`) successfully implemented the email verification flow. Key takeaways include the refactoring of `auth_service.py` to use custom exceptions and the creation of a dedicated frontend page for verification. The backend now has a configurable frontend URL.
- **New/Modified Files from Previous Story:**
    - `backend/app/api/schemas.py` (NEW)
    - `backend/app/core/auth_service.py` (MODIFIED)
    - `backend/app/api/v1/auth.py` (MODIFIED)
    - `backend/tests/test_main.py` (MODIFIED)
    - `the-ai-helping-tool/app/verify-email/page.tsx` (NEW)
- **Project Structure Alignment:** The new components for login will follow the established pattern: a new API endpoint in `backend/app/api/v1/auth.py`, business logic in `backend/app/core/auth_service.py`, and a new frontend page/component for the login form under `the-ai-helping-tool/app/login/`.
- **Technical Debt:** The integration of a full testing framework (Jest/Cypress) is still a deferred item. While unit tests are being added, E2E testing is not yet in place.

### References
- [Source: docs/epics.md#story-14-secure-user-login-and-session-management]
- [Source: docs/architecture.md]
- [Source: docs/prd.md]

## Dev Agent Record

- **Context Reference:** docs/sprint-artifacts/1-4-secure-user-login-and-session-management.context.xml
- **Agent Model Used:** Gemini
- **Debug Log References:**
    - Implemented login endpoint: POST /api/v1/auth/login
    - Used Auth0 for credential validation and JWT issuance.
    - Added user entry to local DB if not present after successful Auth0 login.
    - Tests for login endpoint added in backend/tests/test_main.py.
    - Added unit tests for `AuthService.login` logic in backend/tests/test_auth_service.py.
    - Implemented login UI components in Next.js.
    - Implemented session management in frontend, including token storage and authenticated fetch.
    - Added component tests for `LoginForm.tsx`.
    - Added API integration tests for the login endpoint, including protected route access.
    - Implemented token expiration and renewal logic in `the-ai-helping-tool/services/authService.ts`. The `authenticatedFetch` function now intercepts 401 Unauthorized responses, attempts to refresh the token via `/api/v1/auth/refresh`, and retries the original request with the new token. If refresh fails, the user is logged out and redirected to the login page.
- **Completion Notes List:**
    - Completed implementation and testing of the backend login endpoint.
    - All related unit/integration tests passed.
    - Unit tests for `AuthService.login` also passed, ensuring core logic is robust.
    - Implemented the basic login UI, integrated with the backend API.
    - Session management for token storage and authenticated requests implemented.
    - Component tests for `LoginForm.tsx` passed successfully.
    - API integration tests for the login endpoint and protected route also passed.
    - Manual verification instructions for frontend/backend integration have been provided.
    - API documentation for the login endpoint is automatically generated by FastAPI.
    - Implemented robust token expiration and renewal handling within `authService.ts`, ensuring continuous user sessions even with short-lived access tokens. The `authenticatedFetch` function now gracefully retries requests after refreshing expired tokens, improving user experience by minimizing disruptive logouts.
- **File List:**
    - Modified: backend/app/api/schemas.py
    - Modified: backend/app/core/auth_service.py
    - Modified: backend/app/api/v1/auth.py
    - Modified: backend/tests/test_main.py
    - Added: backend/tests/test_auth_service.py
    - Added: the-ai-helping-tool/app/login/page.tsx
    - Added: the-ai-helping-tool/components/auth/LoginForm.tsx
    - Modified: the-ai-helping-tool/services/authService.ts
    - Added: the-ai-helping-tool/app/dashboard/page.tsx
    - Added: the-ai-helping-tool/components/auth/__tests__/LoginForm.test.tsx
    - Modified: backend/main.py## Change Log

- **2025-12-14:** Initial draft.

