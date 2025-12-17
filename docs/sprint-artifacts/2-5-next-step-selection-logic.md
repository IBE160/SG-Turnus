# Story 2.5: Next Step Selection Logic

**As the AI engine,**
I want to select and present the single most helpful next step to the user,
**So that** I can optimize for minimal cognitive load, active engagement, and immediate payoff.

## Acceptance Criteria

**Given** the detected intent, inferred user state, and confidence levels
**When** the system determines the optimal next interaction
**Then** it selects a single, clear, active, relevant, and recoverable next step for the user.
**And** this selection prioritizes minimal cognitive load and immediate payoff.

## Prerequisites

- Story 2.1: Input Processing and Signal Extraction
- Story 2.2: Task Intent Detection
- Story 2.3: User State Inference
- Story 2.4: Uncertainty Handling and Calibration

## Technical Notes

- Covers FR5. This is the core decision-making logic of the clarity engine.
- **Architectural Reference**: The "Novel Architectural Patterns" section in `architecture.md` (specifically "AI Orchestration Pattern: 'The Clarity Engine'") states: "Based on the updated context, a 'Planner' module dynamically selects the most appropriate AI capability module and the best interaction pattern... to generate the single most helpful next step." This story is the implementation of that "Planner" module.

---
## Requirements Context Summary

This story, "Next Step Selection Logic," is the centerpiece of Epic 2, "Core AI - Clarity Engine." It directly implements the "Planner" module described in the architecture, which is responsible for the core decision-making of the AI.

Building upon the outputs of the previous stories in this epic (intent detection, user state inference, and uncertainty handling), this story's logic will take all available context and make the critical decision of what to do next for the user. The goal is to provide a single, clear, and highly valuable next step, avoiding overwhelming the user while maximizing engagement and learning.

## Structure Alignment and Lessons Learned

Implementation will follow the "AI Orchestration Pattern" from `architecture.md`. The "Planner" will be a new service within the Python backend's core logic.

## Acceptance Criteria

### Given the detected intent, inferred user state, and confidence levels:

- **When** the system determines the optimal next interaction
  - **Then** it selects a single, clear, active, relevant, and recoverable next step for the user.
  - **And** this selection prioritizes minimal cognitive load and immediate payoff.

## Tasks & Subtasks

### 1. Define "Next Step" Data Structure

- [ ] In `backend/app/schemas/`, define a Pydantic schema for the "Next Step". This should include fields for `ai_module` (e.g., 'SummarizationModule'), `interaction_pattern` (e.g., 'Micro-Explanation'), and any necessary parameters for the module.
- [ ] Ensure the structure is flexible enough to accommodate all planned AI capabilities and interaction patterns.

### 2. Implement the Planner Service

- [ ] Create a new file `backend/app/core/planner_service.py`.
- [ ] Implement a `PlannerService` class within this file.
- [ ] Create a primary method, e.g., `select_next_step(intent: str, user_state: str, confidence: float) -> NextStepSchema`.

### 3. Develop the Rule-Based Selection Logic

- [ ] Within the `select_next_step` method, implement a rule-based system to determine the next step.
- [ ] The rules should map combinations of `intent`, `user_state`, and `confidence` to a specific `ai_module` and `interaction_pattern`.
- [ ] Example rule: `if intent == 'Clarification' and user_state == 'confused' and confidence > 0.8: return NextStep(ai_module='QAModule', interaction_pattern='AnchorQuestion')`.
- [ ] The initial ruleset should cover the primary user journeys and intents.
- [ ] **Testing:** Write extensive unit tests in `backend/tests/test_planner_service.py` using `pytest`. Test various combinations of inputs and assert that the correct `NextStep` is returned.

### 4. Integrate Planner into the "Clarity Engine" Loop

- [ ] In the main orchestration logic (likely a high-level service that coordinates the AI modules), import and instantiate the `PlannerService`.
- [ ] After the `infer` step (where intent and user state are determined), call the `planner_service.select_next_step(...)` method.
- [ ] The output of the planner will then be used to call the appropriate AI module in the `act` step.
- [ ] **Testing:** Write integration tests to ensure the planner is called correctly within the orchestration flow and that its output is correctly used.

### 5. API and Documentation

- [ ] The main API endpoint that drives the Clarity Engine will now return the result of the selected "next step". No new endpoints are likely needed for this story, but the response body of the existing endpoint will be dependent on the planner's output.
- [ ] Ensure any changes to API responses are reflected in the OpenAPI documentation.

## Change Log

| Date         | Version | Description        | Author |
| :----------- | :------ | :----------: ----- |
| 2025-12-17   | 1.0     | Initial draft      | Gemini |
