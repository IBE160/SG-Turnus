# The AI Helping Tool

This project is a student exam project demonstrating development with AI. The goal of this project is to provide a polished, stable, and professional-looking MVP of a tool that helps students with their study materials.

## Tech Stack

*   **Backend:** FastAPI (Python)
*   **Frontend:** Next.js (React)

## How to Start

### Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the backend server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### Frontend

1.  Navigate to the `the-ai-helping-tool` directory:
    ```bash
    cd the-ai-helping-tool
    ```
2.  Install the required dependencies:
    ```bash
    npm install
    ```
3.  Start the frontend development server:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

## What Works

*   The user can navigate to the dashboard to see a list of their study materials.
*   The user can generate summaries, flashcards, and quizzes from their study materials.
*   The application uses a mocked authentication system, so users are automatically logged in.

## What is Mocked

*   **Authentication:** The authentication system is mocked. A dummy token is used to simulate an authenticated user.
*   **Study Materials:** The study materials are mocked. The application does not actually upload or process any files.
*   **AI Functionality:** The AI-powered features (summaries, flashcards, quizzes) are mocked. The application returns pre-defined data instead of using a real AI model.

## Known Limitations

*   The database is currently disabled.
*   User registration and login are not implemented.
*   File uploads are not functional.
*   The sharing and export features have been removed.

## Suggested Future Work

*   Implement a full authentication system with user registration and login.
*   Integrate a real database to store user data and study materials.
*   Implement file uploads to allow users to upload their own study materials.
*   Integrate a real AI model to provide accurate and dynamic content generation.
*   Implement the sharing and export features.
*   Add more study tools, such as a note-taking feature or a study planner.