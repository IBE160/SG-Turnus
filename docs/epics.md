# Product Backlog: Epics and User Stories

**Version:** 1.0
**Author:** BMM Product Manager
**Date:** 2025-12-04

This document translates the product requirements and architecture into a prioritized backlog of work.

---

## EPIC 1: Foundational Setup (MVP)

**Description:** This epic covers the essential, non-user-facing technical setup required to build, deploy, and run the application. It's the groundwork upon which all features are built.

### User Stories

**Story 1.1: Initialize Frontend Application**
- **As a** developer,
- **I want to** set up a new Flutter project with the standard folder structure,
- **so that** we have a clean, consistent foundation for building the UI and client-side logic.
- **Acceptance Criteria:**
  - A new Flutter project is created in the repository.
  - The project follows the standard Flutter folder structure.
  - The "Growth" color theme and typography from the UX spec are configured.
  - The app compiles and runs on both an Android emulator and an iOS simulator.

**Story 1.2: Initialize Backend Service**
- **As a** developer,
- **I want to** configure a serverless application with a "Hello World" Lambda function and an API Gateway endpoint,
- **so that** the frontend has a live endpoint to connect to for initial development and testing.
- **Acceptance Criteria:**
  - An AWS API Gateway endpoint is created.
  - A Python-based Lambda function is created and connected to the gateway.
  - Invoking the endpoint via a tool like Postman returns a `200 OK` with a `{ "message": "Hello World" }` body.
  - All infrastructure is defined as code (e.g., using AWS SAM or Terraform).

---

## EPIC 2: The "Instant Clarity" Loop (MVP)

**Description:** This is the core value proposition of the MVP. It covers the end-to-end user journey for submitting a text-based query and receiving a single, actionable response.

### User Stories

**Story 2.1: Text Input**
- **As a** student,
- **I want to** see a clear input field and type my question into it,
- **so that** I can easily ask for help when I'm stuck.
- **Acceptance Criteria:**
  - The main screen displays a text input field as per the UX specification.
  - The user can tap the field to bring up the on-screen keyboard.
  - The user can type and edit text in the field.

**Story 2.2: Submit Query & Receive Feedback**
- **As a** student,
- **I want to** tap a "Get Clarity" button and see a processing animation,
- **so that** I know my request is being handled.
- **Acceptance Criteria:**
  - A primary action button ("Get Clarity") is present.
  - Tapping the button when the input field has text triggers the API call to `POST /api/v1/clarity`.
  - The request body is correctly formatted: `{ "inputType": "text", "content": "..." }`.
  - Upon submission, the UI displays the "Spinning Hat" loading animation as per the UX spec.

**Story 2.3: Display Clarity Response**
- **As a** student,
- **I want to** see the single, concise actionable sentence on my screen,
- **so that** I can immediately understand my next step.
- **Acceptance Criteria:**
  - On a successful API response, the loading animation is replaced by the clarity result screen.
  - The `clarity` string from the API response is displayed prominently.
  - The entire round trip, from tapping "Get Clarity" to seeing the result, takes less than 2 seconds (NFR1).
  - If the API returns an error (e.g., `AI_TIMEOUT`), the specific error message from the UX spec is displayed.

---

## EPIC 3: Multi-Modal Input (MVP)

**Description:** This epic expands the core loop to include the camera and microphone, delivering on the promise of a truly versatile and accessible tool.

### User Stories

**Story 3.1: Camera Input**
- **As a** student,
- **I want to** tap a camera icon, take a photo of my textbook, and use the text from it as my input,
- **so that** I don't have to manually type out long passages.
- **Acceptance Criteria:**
  - A camera icon is present on the input screen.
  - Tapping the icon prompts for camera permissions (if not already granted).
  - The app opens the device camera.
  - After taking a picture, the app sends the image data to the backend (`inputType`: `image`).
  - The backend returns either the extracted text for confirmation or an `IMAGE_UNREADABLE` error, which is displayed to the user.

**Story 3.2: Voice Input**
- **As a** student,
- **I want to** tap a microphone icon, record myself speaking, and use the transcription as my input,
- **so that** I can ask questions hands-free while studying.
- **Acceptance Criteria:**
  - A microphone icon is present on the input screen.
  - Tapping the icon prompts for microphone permissions (if not already granted).
  - The app begins recording audio and provides visual feedback that it's listening.
  - Tapping again stops the recording and sends the audio data to the backend (`inputType`: `audio`).
  - The backend returns either the transcribed text for confirmation or an `AUDIO_UNCLEAR` error, which is displayed to the user.

---

## EPIC 4: Growth & User Persistence (Post-MVP)

**Description:** This epic covers features that build on the core loop, adding depth, convenience, and personalization. This work is to be prioritized after the MVP is validated.

### User Stories

**Story 4.1: Expand for Detail**
- **As a** user,
- **I want to** have an option to request a more detailed explanation after getting my initial clarity,
- **so that** I can dive deeper into a topic if I need more context.
- **Acceptance Criteria:**
  - A subtle "Expand Detail" button or gesture is available on the clarity result screen.
  - Activating it triggers a new API call to get more detailed content.
  - The UI displays the detailed content without losing the context of the initial clarity step.

**Story 4.2: Basic User Accounts**
- **As a** user,
- **I want to** create an account using my Google or Apple ID,
- **so that** my history can be saved and synced across devices.
- **Acceptance Criteria:**
  - The app provides an optional "Sign In" flow.
  - Users can authenticate using OAuth with Google and Apple.
  - Upon successful login, a user record is created in the DynamoDB database.

**Story 4.3: Session History**
- **As a** logged-in user,
- **I want to** see a list of my past clarity events,
- **so that** I can easily refer back to topics I've worked on.
- **Acceptance Criteria:**
  - A new "History" screen is available for logged-in users.
  - Each clarity event (input and output) is saved to DynamoDB for logged-in users.
  - The History screen displays a chronological list of past events.
