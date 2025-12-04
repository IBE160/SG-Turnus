# Architecture Specification: The AI Helping Tool

**Version:** 1.0
**Author:** BMM Architect
**Date:** 2025-12-04

## 1. Architectural Drivers

This architecture is designed to meet the primary business and technical requirements outlined in the PRD and UX Design Specification. The key drivers are:

- **Performance:** The core "Instant Clarity" loop must complete in **under 2 seconds**. This dictates a low-latency, high-performance design.
- **Scalability:** The system must handle **10,000 users** at launch and scale efficiently.
- **Cross-Platform:** The user experience must be consistent across **iOS, Android, and Web**.
- **Multi-Modal Input:** The system must process **text, image, and audio** inputs seamlessly.
- **Rapid Development:** The MVP must be delivered efficiently, prioritizing the core value proposition.
- **Frictionless UX:** The design must support the "Calm & Focused" and "Effortless Entry" principles defined in the UX specification.

## 2. System Architecture: C4 Model

The proposed architecture is a **client-server model** utilizing a serverless backend to orchestrate multiple specialized AI services. This provides maximum scalability and performance while minimizing operational overhead.

### 2.1 Level 1: System Context Diagram

This diagram shows how "The AI Helping Tool" fits into its environment and who interacts with it.

```mermaid
graph TD
    subgraph "The World"
        A[Student (User)]
    end

    subgraph "AI Services"
        LLM[LLM Service (e.g., Gemini)]
        OCR[OCR Service (e.g., AWS Textract)]
        STT[Speech-to-Text Service (e.g., AWS Transcribe)]
    end

    subgraph "Our System"
        B(AI Helping Tool)
    end

    A -- "Submits query (text, photo, voice)" --> B
    B -- "Receives actionable clarity" --> A
    
    B -- "Sends text for analysis" --> LLM
    B -- "Sends image for text extraction" --> OCR
    B -- "Sends audio for transcription" --> STT

    style B fill:#198754,stroke:#333,stroke-width:2px,color:#fff
```

### 2.2 Level 2: Container Diagram

This diagram decomposes the "AI Helping Tool" system into its major deployable components (containers).

```mermaid
graph TD
    A[Student (User)]

    subgraph "Our System Boundary"
        direction LR
        
        subgraph "Client Tier"
            C[Mobile & Web App]
        end

        subgraph "Backend Tier (Serverless on AWS)"
            D{API Gateway}
            E[Clarity Function (Lambda)]
        end

        C -- "1. Sends query via HTTPS" --> D
        D -- "2. Routes to Lambda" --> E
        E -- "3a. Orchestrates AI calls" --> F((AI Services))
        F -- "3b. Returns results" --> E
        E -- "4. Returns response" --> D
        D -- "5. Relays response" --> C
    end

    subgraph "External AI Services Boundary"
        F
    end
    
    A -- "Interacts with" --> C

    style C fill:#e8f5e9,stroke:#198754
    style D fill:#f9f9f9,stroke:#333
    style E fill:#f9f9f9,stroke:#333
```

**Container Descriptions:**

- **Mobile & Web App:** The user-facing application built on a cross-platform framework. Responsible for all UI, device interactions (camera, mic), and communication with the backend.
- **API Gateway:** The single entry point for all client requests. It handles routing, authentication (post-MVP), and throttling.
- **Clarity Function (Lambda):** A serverless function that contains the core business logic. It receives the user's query, orchestrates the necessary calls to the downstream AI services, and formats the final response.
- **AI Services:** A logical grouping of external, third-party services providing the core intelligence:
    - **LLM Service:** Generates the "actionable clarity" step.
    - **OCR Service:** Extracts text from images.
    - **Speech-to-Text Service:** Transcribes audio recordings.

## 3. Technology Stack

The technology stack is chosen to align with the architectural drivers.

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | **Flutter** | **Cross-Platform:** Single codebase for iOS, Android, and Web ensures consistency and development speed. **Performance:** Compiles to native code for high performance. **UI:** Excellent integration with the chosen Material Design system. |
| **Backend** | **AWS Lambda (Python)** | **Scalability:** Inherently scalable to meet user demand without server management. **Cost-Effective:** Pay-per-use model is ideal for a new product. **Ecosystem:** Native integration with other proposed AWS services. Python is excellent for data handling and AI tasks. |
| **API Layer**| **AWS API Gateway**| **Managed & Scalable:** Provides a robust, secure, and scalable entry point for the backend. **Integration:** Seamlessly connects to AWS Lambda. |
| **AI Services** | | |
| ↳ **OCR** | **AWS Textract** | **Accuracy & Scalability:** A powerful, managed OCR service that integrates easily with Lambda. |
| ↳ **Transcription** | **AWS Transcribe**| **Managed Service:** High-quality speech-to-text without managing infrastructure. Integrates easily with Lambda. |
| ↳ **LLM** | **(Abstracted) e.g., Gemini API** | An interface will be created to abstract the specific LLM provider, allowing for flexibility to change models based on cost, performance, or quality. |
| **Database (Post-MVP)** | **Amazon DynamoDB** | **Scalability & Performance:** A fully managed NoSQL database that offers low-latency performance at any scale, perfect for user session history and accounts. |


## 4. API Design (MVP)

The core of the system is a single, well-defined API endpoint.

### `POST /api/v1/clarity`

- **Description:** Receives a user query, processes it through the necessary AI services, and returns an actionable result.
- **Request Body:**
  ```json
  {
    "inputType": "text" | "image" | "audio",
    "content": "<string>"
  }
  ```
  - `inputType`: Specifies the type of content being sent.
  - `content`: Base64-encoded string for `image` and `audio`; plain string for `text`.

- **Success Response (200 OK):**
  ```json
  {
    "clarity": "The single, concise, actionable next step to unblock the user."
  }
  ```

- **Error Responses:**
  - `400 Bad Request` (`IMAGE_UNREADABLE`): If image is unreadable.
  - `400 Bad Request` (`AUDIO_UNCLEAR`): If audio is unintelligible.
  - `504 Gateway Timeout` (`AI_TIMEOUT`): If the AI processing takes too long.

## 5. Next Steps

This architecture provides the blueprint for the Solutioning and Implementation phases. The next steps are:
1.  **Refinement & Review:** Share with PM and TEA for feedback.
2.  **Epic & Story Creation:** Decompose the work required to build these components.
3.  **Proof of Concept:** A technical spike may be required to validate the end-to-end performance of the "clarity loop" through the proposed stack.
