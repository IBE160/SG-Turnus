# Story 1.2: user-account-creation

Status: ready-for-dev

## Story

As a new user,
I want to create a personal account using my email and a password,
so that I can have a personalized and secure experience.

## Acceptance Criteria

1. Given a user is on the "Sign Up" page
2. When they enter a valid email and a strong password (e.g., 8+ characters, with uppercase, lowercase, number, and special character)
3. And they submit the form
4. Then a new user account is created in the database.
5. And an email is sent to the user with a verification link.
6. And the user is shown a message to check their email for verification.
7. And the password is securely hashed and salted before being stored.

## Tasks / Subtasks

- [ ] **Task 1: Frontend - Create Sign Up UI** (AC: 1, 2, 6)
  - [ ] Create a new page/route for `/signup`.
  - [ ] Build the Sign Up form using Material UI components (`TextField`, `Button`).
  - [ ] Implement form validation for email format and password strength.
  - [ ] Display a confirmation message after submission, prompting the user to check their email.
- [ ] **Task 2: Backend - Implement Registration Endpoint** (AC: 4, 5, 7)
  - [ ] Create the `POST /api/v1/auth/register` endpoint in the Python backend.
  - [ ] Integrate with the managed authentication provider to create the user.
  - [ ] After the auth provider confirms creation, create a corresponding user record in the local PostgreSQL `users` table.
  - [ ] Ensure the password hashing is handled by the managed auth provider.
- [ ] **Task 3: Backend - Implement Email Verification** (AC: 5)
  - [ ] Integrate the Resend email service.
  - [ ] Trigger the verification email send from the registration endpoint.
  - [ ] Create a separate endpoint (e.g., `/api/v1/auth/verify-email`) to be called when the user clicks the link in the email.
- [ ] **Task 4: Testing** (AC: 1-7)
  - [ ] Write unit tests for the frontend form component.
  - [ ] Write integration tests for the `/api/v1/auth/register` backend endpoint.
  - [ ] Write an E2E test that simulates the entire sign-up and email verification flow.

## Dev Notes

### Learnings from Previous Story

**From Story 1.1 (Status: review)**

- **Project Initialized**: Next.js project 'the-ai-helping-tool' is set up.
- **Git Initialized**: Git was manually initialized in the project root.
- **Dependencies**: Unintended Tailwind CSS dependencies were removed.
- **Directory Structure**: Standard Next.js structure is in place, with `app`, `components`, `lib`, and `services` directories.
- **Verification**: The initial setup runs (`npm run dev`) and lints (`npm run lint`) without errors.

[Source: docs/EPIC-1-STORY-1.1.md#Dev-Agent-Record]

### Implementation Details
- **Relevant architecture patterns and constraints:**
  - **Authentication:** Use a managed provider (e.g., Auth0, Clerk). The frontend will handle the UI, and the backend will validate JWTs. (Source: `docs/architecture.md#Security Architecture`, `docs/sprint-artifacts/tech-spec-epic-1.md#Services and Modules`)
  - **API:** RESTful API, with a `POST /api/v1/auth/register` endpoint. (Source: `docs/sprint-artifacts/tech-spec-epic-1.md#APIs and Interfaces`)
  - **Database:** PostgreSQL for user data. (Source: `docs/architecture.md#Data Persistence`)
  - **Data Model:** `users` table with `auth_provider_id` and `email`. (Source: `docs/sprint-artifacts/tech-spec-epic-1.md#Data Models and Contracts`)
  - **Email Service:** Use Resend for verification emails. (Source: `docs/architecture.md#Email Service`)
- **Source tree components to touch:**
  - **Frontend:** Create UI components for the "Sign Up" form under `the-ai-helping-tool/components/auth/`.
  - **Frontend:** Create a service to communicate with the backend API at `the-ai-helping-tool/services/authService.ts`.
  - **Backend:** Implement the `Authentication Service` and the `/api/v1/auth/register` endpoint.
- **Testing standards summary:**
  - Unit tests for backend services (Pytest).
  - Integration tests for the API endpoint.
  - E2E test for the full registration flow (Cypress/Playwright). (Source: `docs/sprint-artifacts/tech-spec-epic-1.md#Test Strategy Summary`)

### Project Structure Notes

- **Learnings from previous story (1.1):** The project is a standard Next.js application. The `components`, `lib`, and `services` directories have been created.
- **Alignment:** The new components and services for authentication should be placed in the existing structure (e.g., `components/auth`, `services/authService.ts`). No conflicts detected.

### References

- [Source: docs/epics.md#Story 1.2: User Account Creation]
- [Source: docs/architecture.md#Security Architecture]
- [Source: docs/sprint-artifacts/tech-spec-epic-1.md]

## Dev Agent Record

### Context Reference

- [docs/sprint-artifacts/1-2-user-account-creation.context.xml]

### Agent Model Used

gemini/gemini-pro

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-12-12: Initial draft created by SM agent.