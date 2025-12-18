### Story 3.1: Automated Summary Generation

As a user,
I want the system to automatically generate concise and accurate summaries from my uploaded study materials,
So that I can quickly grasp the main points.

**Acceptance Criteria:**

**Given** an uploaded study material (text) and a request for summarization (either direct or inferred intent)
**When** the system processes the material
**Then** it generates a summary that accurately reflects the core content.
**And** the summary can be adjusted for detail level (e.g., brief, detailed).
**And** the summary is presented in a readable format.

**Prerequisites:** Epic 2 (specifically, input processing and intent detection)

**Technical Notes:** Covers FR7. This involves text summarization techniques, likely using abstractive or extractive methods based on an LLM or similar AI model.