# E2E Runbook and Status for User Account Creation

## 1. Overview
This document outlines the steps to set up and run the End-to-End (E2E) tests for the User Account Creation feature (Story 1.2). It also tracks the current status and known issues related to the E2E testing environment.

## 2. Prerequisites
- Node.js (with npm) installed for the frontend application.
- Python (with venv and pip) installed for the backend application.
- Cypress installed in the `the-ai-helping-tool` directory (`npm install cypress`).
- The necessary environment variables for Auth0 and Resend should be set for the backend.
  - `AUTH0_DOMAIN`, `AUTH0_MANAGEMENT_CLIENT_ID`, `AUTH0_MANAGEMENT_CLIENT_SECRET`
  - `RESEND_API_KEY`
  - `NEXT_PUBLIC_EMAIL_VERIFICATION_URL` (e.g., `http://localhost:3000`)

## 3. Starting the Applications

### 3.1 Start Backend (FastAPI)
The backend requires a database. For E2E tests, it can use an in-memory SQLite database if `E2E_TEST_MODE=true` is set.

1.  Navigate to the project root directory.
2.  Run the following command to start the backend in the background:
    ```bash
    nohup bash -c "export PYTHONPATH=$(pwd) AUTH0_DOMAIN=dummy AUTH0_MANAGEMENT_CLIENT_ID=dummy AUTH0_MANAGEMENT_CLIENT_SECRET=dummy RESEND_API_KEY=dummy NEXT_PUBLIC_EMAIL_VERIFICATION_URL=http://localhost:3000 E2E_TEST_MODE=true && source backend/venv/bin/activate && uvicorn backend.main:app --reload" > backend_nohup.out 2>&1 & echo $!
    ```
    Note the PID (the number printed after the command) for stopping the process later.

### 3.2 Start Frontend (Next.js)
The frontend relies on the backend API.

1.  Navigate to the project root directory.
2.  Run the following command to start the frontend in the background:
    ```bash
    sleep 5 && nohup bash -c "cd the-ai-helping-tool && npm run dev" > frontend_nohup.out 2>&1 & echo $!
    ```
    Note the PID (the number printed after the command) for stopping the process later.

## 4. Running E2E Tests (Cypress)

1.  Ensure both frontend and backend applications are running and accessible (wait at least 15-20 seconds after starting the frontend).
2.  Navigate to the `the-ai-helping-tool` directory.
3.  Run the Cypress tests:
    ```bash
    npx cypress run
    ```

## 5. Stopping the Applications

1.  Identify the PIDs of the background processes (from section 3.1 and 3.2).
2.  Kill the processes using their PIDs:
    ```bash
    kill <backend_pid> <frontend_pid>
    ```
    Or, if you stored the process group IDs (PGIDs), you can use:
    ```bash
    kill -- -<backend_pgid> && kill -- -<frontend_pgid>
    ```

## 6. E2E Test Status (User Account Creation - Story 1.2)

-   **Last Run Date:** 2025-12-14
-   **Outcome:** Failing
-   **Key Issue:** `ECONNREFUSED` - Cypress cannot connect to `http://localhost:3000/signup`.
    -   **Cause (Investigation):** The Next.js development server (`npm run dev`) does not appear to be robustly staying alive or serving requests when run in the background using `nohup` via `bash -c ... &` within this CLI environment.
    -   **Current Status:** Unresolved environmental issue. All code-level issues for Story 1.2 have been addressed, and unit/integration tests are passing. The E2E test failure is a process management/environmental blocker.

-   **Recommendations:**
    -   Further investigation is required to stabilize the Next.js development server's background execution in this environment.
    -   Consider running frontend and backend manually in separate terminals if automated background execution continues to be problematic.
    -   Explore alternative process management tools (e.g., `pm2`, `forever`) if available in the environment, or if a `docker-compose` setup is introduced.
    -   The Cypress tests themselves have been enhanced to cover duplicate email registration and client-side password validation, and are ready to pass once the environment is stable.
