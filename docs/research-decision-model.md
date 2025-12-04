# Research Findings: Decision Model for Determining the “Single Most Helpful Next Step”
1. Overview

This document outlines a structured decision model for how the Zero-Friction Instant Clarity Engine can infer and deliver the “single most helpful next step” for any user input. The model is designed to operate under uncertainty, adapt to different input types, and maintain ultra-low cognitive load for the user.

The goal is to create a consistent inference pipeline while preserving flexibility for diverse learning materials and user states.

2. Task Classification Framework

The system must detect what type of task the user implicitly needs. Core task categories include:

Clarification
The user does not understand a concept in the material.

Summarization
The user needs a structured, shorter form of the input.

Active Recall
The user benefits from answering a targeted question.

Problem Solving
The input contains a question, problem, or exercise requiring reasoning steps.

Concept Linking
The material contains multiple interconnected ideas requiring structural mapping.

Misconception Correction
The user input indicates misunderstanding or incomplete knowledge.

Each category should be assigned a confidence score.

3. Signals Extracted From Input

The engine extracts signals from the user’s submission, including:

Lexical indicators (e.g., “Why,” “Explain,” “I don’t get”).

Structure (paragraph, formula, notes, screenshots).

Content density and complexity.

Presence of diagrams, lists, or problems.

Implicit user intent inferred from phrasing.

Signals are weighted and contribute to category scoring.

4. Inference of User State

The engine must infer a provisional user state to tailor the next step:

Confused: Needs grounding or clarification.

Curious: Ready for deeper engagement.

Overloaded: Needs simplification and low effort.

Time-limited: Requires ultra-short, high-yield guidance.

Uncertain: Needs small calibration step.

This estimation is probabilistic and must tolerate ambiguity.

5. Uncertainty Handling Strategy

When confidence is low:

Prefer calibration questions (one-second checks).

Use exploratory phrasing ("Let's check whether this idea is central").

Provide fallback options internally without exposing them.

Avoid definitive or evaluative tone.

When confidence is high:

Provide a decisive, active step.

Keep phrasing simple and grounded.

6. Next-Step Selection Logic

The next step must satisfy all of the following:

Minimal cognitive load: One small, clear action.

Active engagement: Requires a short response or reflection.

Immediate payoff: Generates clarity or confirmation.

Relevance: Closely tied to the core idea extracted from the input.

Recoverability: User can easily redirect if incorrect.

Examples of next steps:

“What do you think this term means in your own words?”

“Select which of these interpretations best fits the passage.”

“This paragraph hinges on one idea. Let’s anchor it first: what is the key claim?”

“Here is the core assumption. Before we go further, does this match what you understood?”

7. Example Decision Flows
Example A: User pastes a dense paragraph.

Detected: Clarification + Active Recall.
Next step: Anchor question about the central idea.

Example B: User pastes a photo of a math problem.

Detected: Problem Solving.
Next step: Identify given information or restate the problem.

Example C: Fragmented screenshot.

Confidence low.
Next step: One-second calibration question to clarify domain.
