# The AI Helping Tool - Product Requirements Document

**Author:** BIP
**Date:** 2025-12-04
**Version:** 1.0

---

## Executive Summary

The "AI Helping Tool" is an AI-powered study partner designed to dramatically improve learning efficiency for high school, university, and adult learners. Its primary purpose is to provide **instant clarity and momentum** by transforming overwhelming study materials into manageable, actionable steps. The core strategy is to **actively reduce the cognitive load** on students, positioning the tool as an intelligent partner that makes learning frictionless and builds momentum through a "Zero-Friction Instant Clarity Engine."

### What Makes This Special

- **Focus on Momentum, Not Just Features:** The primary goal is to reduce cognitive load and create forward momentum for the user. Every design choice is optimized for speed and clarity.
- **Multi-Modal Input:** Accepting photos and voice notes in addition to text makes the tool radically accessible and useful in real-world study situations.
- **Simplicity by Default:** The core experience is one input, one clear output. Resists feature bloat to maintain a zero-friction loop.

---

## Project Classification

**Technical Type:** mobile_app
**Domain:** edtech
**Complexity:** medium

Based on the mobile-first approach and the focus on student learning, this project is classified as a **mobile_app** in the **edtech** domain. The complexity is **medium** due to the need for AI integration and a robust, scalable backend, balanced by a intentionally simple user-facing feature set.

{{#if domain_context_summary}}

### Domain Context

{{domain_context_summary}}
{{/if}}

---

## Success Criteria

Success is defined by becoming the student's first instinct when they feel stuck or overwhelmed. The key metric is not just usage, but impact on the user's learning momentum and confidence.

- **User-Centric Outcomes:**
  - **Reduced Time-to-Clarity:** The tool is successful if it measurably shortens the time from a user feeling confused to having a clear, actionable next step.
  - **High "Stuck Rate" Resolution:** Success is measured by the frequency with which users turn to the app when they are stuck and successfully get back on track.
  - **Qualitative Feedback:** User feedback consistently mentions reduced study-related anxiety and increased confidence.
  - **User Love:** The tool becomes an indispensable part of the user's study process, demonstrated by high retention during academic seasons (e.g., exam periods).

### Business Metrics

The primary business metric is the delivery of our core value proposition.

- **Primary Metric: Clarity Events:** A "clarity event" is logged every time a user submits input and receives an actionable output. This is our core measure of value delivered.
- **Secondary Metrics:**
  - **Activation Rate:** Percentage of new users who complete at least one clarity event within their first session.
  - **Seasonal Retention:** High retention rates measured during peak academic periods (mid-terms, final exams).
  - **Input Method Mix:** Tracking the usage of text vs. photo vs. voice input to ensure we are delivering on the multi-modal promise.

---

## Product Scope

### MVP - Minimum Viable Product

The MVP is ruthlessly focused on delivering the core "Instant Clarity" promise with maximum speed and accessibility. It must prove the core value proposition and nothing more.

- **Single-Action "Instant Clarity" Input:** A universal, simple input field for text.
- **Camera-Based Capture:** Allow users to snap a photo of a prompt, textbook page, or notes. The text is extracted and used as input.
- **Voice Input:** Allow users to record a short voice note. The transcribed text is used as input.
- **Ultra-Short, Actionable Output:** The AI's default response is a single, concise next step (5-7 words) designed to unblock the user immediately.
- **No Accounts Required:** The app is fully usable in a "guest mode" to eliminate signup friction.

### Growth Features (Post-MVP)

After validating the core loop, growth features will add depth and convenience without compromising the initial simplicity.

- **"Expand for Detail" Option:** Allow users to optionally request a more detailed explanation, summary, or a list of sub-tasks after receiving their initial "instant clarity" step.
- **Session History:** A simple, chronological list of past "clarity events" for the user to reference.
- **Basic User Accounts:** Optional accounts (e.g., sign-in with Google/Apple) to allow session history to sync across devices (mobile and web).
- **Improved Input Parsing:** Enhanced context detection from images (e.g., recognizing diagrams vs. text).

### Vision (Future)

The long-term vision is for the tool to evolve from a reactive helper into a proactive, personalized learning partner that anticipates the user's needs.

- **Proactive Suggestions:** The AI begins to understand the user's study context and proactively suggests next steps or identifies connections between different pieces of information.
- **Automated Revision Schedules:** Based on topics the user frequently struggles with (identified via repeated inputs), the tool automatically generates spaced repetition schedules.
- **Deep Contextual Understanding:** The AI maintains context across multiple user inputs, building a knowledge graph of the user's subject matter to provide more insightful assistance.
- **Predictive Assistance:** The tool anticipates future challenges, such as upcoming exams or deadlines, and suggests a plan to tackle them.

---

{{#if domain_considerations}}

## Domain-Specific Requirements

{{domain_considerations}}

This section shapes all functional and non-functional requirements below.
{{/if}}

---

## Innovation & Novel Patterns

The core innovation of this product is not a single technical feature, but a novel interaction pattern focused on radical simplicity and cognitive offloading.

- **"Intervention-as-a-Service":** The tool's primary function is to intervene at the precise moment of cognitive friction. It acts as an external executive function for the user, providing the minimum necessary prompt to overcome a mental block and rebuild momentum.
- **Cognitive Offloading:** Unlike tools that aim to automate entire workflows, this tool offloads only the single, highest-friction task: "What do I do next?". This preserves the user's engagement with the material while removing the primary source of procrastination.

### Validation Approach

The core hypothesis—that a single, actionable step is more effective at reducing cognitive load than a comprehensive summary—will be validated with a clear A/B test.

- **Hypothesis:** Users who receive a single, concise action will report lower cognitive load and resume their tasks faster than users who receive a standard summary.
- **Methodology:**
  - **Group A (Control):** Submits a confusing prompt and receives a standard 3-sentence AI-generated summary.
  - **Group B (Treatment):** Submits the same prompt and receives the ultra-short, "one clear action" output.
- **Metrics:**
  - **Quantitative:** Measure the time from receiving the output to taking the next action on their task.
  - **Qualitative:** Post-task survey measuring user-reported confidence and perceived effort.


---

## mobile_app Specific Requirements

These requirements are specific to the nature of the product as a cross-platform mobile application.

- **Development Approach:** The application will be developed using a cross-platform framework (e.g., React Native, Flutter) to ensure simultaneous release on both iOS and Android and to facilitate a fast-follow web application.
- **Offline Mode:** The MVP will require a persistent internet connection, as the core "clarity engine" relies on server-side AI processing. Offline capabilities are out of scope for the initial release.
- **Push Notifications:** There will be no push notifications in the MVP to maintain a zero-friction, user-initiated experience. This feature may be considered post-MVP for features like revision reminders.
- **App Store Compliance:** The application will adhere to the standard submission guidelines for the Apple App Store and Google Play Store, with particular attention to policies regarding user-submitted content and AI generation.

### Platform Support

The application will be supported on the latest major versions of iOS and Android. A responsive web application accessible on modern browsers (Chrome, Safari, Firefox) will be a fast-follow release.

### Device Capabilities

The application will require explicit user permission to access the following device features, which are critical for the multi-modal input promise:
- **Camera:** To allow users to capture images of textbooks, notes, and assignments.
- **Microphone:** To allow users to record voice notes describing their problem.

---

## User Experience Principles

The user experience must be a direct reflection of the core value proposition: reducing cognitive load. The UI should feel calm, clear, and instantly usable.

- **Visual Personality:** Clean, minimalist, and encouraging. The aesthetic should inspire confidence and focus, avoiding the sterile feel of academic tools. Generous use of whitespace is critical.
- **Frictionless Interaction:** The user should never have to think about how to use the tool. The path from opening the app to receiving clarity must be immediate and intuitive.
- **Simplicity as a Feature:** The interface will be radically simple. There will be one primary call to action: the input field. All non-essential UI elements will be removed.

### Key Interactions

The entire user experience is centered around a single, critical interaction loop.

- **The "Instant Clarity" Loop:**
  1.  **Input:** User is presented with a single, inviting input field, with clear icons for text, camera, and voice.
  2.  **Processing:** The app provides immediate visual feedback that the input is being processed, aiming for a near-instant feel.
  3.  **Output:** The single, actionable next step is displayed with maximum clarity and no surrounding clutter. This is the entire screen. Optional secondary actions (like "expand detail" post-MVP) are subtle and do not distract from the primary output.

---

## Functional Requirements

This section defines the complete inventory of user-facing and system capabilities required to deliver the product vision.

**Account & Session**
- **FR1:** Users can use the application's core functionality without creating an account (Guest Mode).
- **FR2:** (Post-MVP) Users can create an account using a social provider (e.g., Google, Apple).
- **FR3:** (Post-MVP) Registered users can log in to their account to access persistent data.
- **FR4:** (Post-MVP) User session history is synchronized across all devices for logged-in users.

**Input & Processing**
- **FR5:** Users can input study-related queries via a text field.
- **FR6:** Users can initiate a query by capturing an image using the device's camera.
- **FR7:** The system can extract and process text from user-provided images.
- **FR8:** Users can initiate a query by recording a short audio clip using the device's microphone.
- **FR9:** The system can transcribe and process text from user-provided audio clips.
- **FR10:** The system can identify and parse key sections (e.g., assignments, due dates, topics) from a user-provided course syllabus.
- **FR11:** The system's AI can analyze the processed input to determine a single, actionable next step.

**Clarity & Output**
- **FR12:** The system must present the primary AI-generated output as a single, concise, actionable sentence.
- **FR13:** (Post-MVP) Users can choose to view a more detailed explanation related to the primary output.
- **FR14:** (Post-MVP) Logged-in users can view a chronological history of their past queries and the results.

**Platform & Device**
- **FR15:** The application must request and obtain user permission before accessing the device camera.
- **FR16:** The application must request and obtain user permission before accessing the device microphone.
- **FR17:** The application must function consistently across supported iOS, Android, and web browser platforms.

---

## Non-Functional Requirements

### Performance

- **NFR1 (Response Time):** The core "clarity loop" (from user input submission to output display) must complete in under 2 seconds to feel "instant."
- **NFR2 (App Launch Time):** The application must cold-start to an interactive state in under 3 seconds on a representative mid-range device.

### Security

- **NFR3 (Data in Transit):** All data transmitted between the client application and backend services must be encrypted using TLS 1.2 or higher.
- **NFR4 (Data at Rest):** Any user-generated content (images, notes) stored on the server must be encrypted at rest.
- **NFR5 (Permissions):** Device permissions (camera, microphone) must be requested just-in-time and not demanded on first app launch.

### Scalability

- **NFR6 (Launch Capacity):** The backend infrastructure must be able to handle the anticipated load of the first 10,000 users in the first week post-launch without performance degradation.

### Accessibility

- **NFR7 (WCAG Compliance):** The application must meet WCAG 2.1 AA standards, ensuring it is usable for students with disabilities. This includes support for screen readers, sufficient color contrast, and keyboard navigation on the web app.

---

_This PRD captures the essence of The AI Helping Tool - giving students instant clarity to overcome study blocks._

_Created through collaborative discovery between BIP and AI facilitator._
