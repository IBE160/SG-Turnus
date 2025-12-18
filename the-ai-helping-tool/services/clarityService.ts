// the-ai-helping-tool/services/clarityService.ts

const API_BASE_URL = '/api/v1';

// --- TypeScript Interfaces (Mirroring Backend Pydantic Schemas) ---
export interface NLPRequest {
  text: string;
}

export enum AIModule {
    SUMMARIZATION = "SummarizationModule",
    FLASHCARD_GENERATION = "FlashcardGenerationModule",
    QUIZ_GENERATION = "QuizGenerationModule",
    QA = "QAModule",
}

export enum InteractionPatternType {
    ANCHOR_QUESTION = "anchor_question",
    MICRO_EXPLANATION = "micro_explanation",
    CALIBRATION_QUESTION = "calibration_question",
    PROBLEM_DECOMPOSITION = "problem_decomposition",
    CONCEPT_SNAPSHOT = "concept_snapshot",
}

export interface NextStep {
    ai_module: AIModule;
    interaction_pattern: InteractionPatternType;
    parameters: Record<string, any>;
}


// --- API Service Functions ---

/**
 * Fetches the next suggested step from the Clarity AI engine based on user input.
 * @param request The NLPRequest containing the user's text.
 * @returns A promise that resolves to a NextStep.
 */
export async function getNextStepSuggestion(request: NLPRequest): Promise<NextStep> {
  const response = await fetch(`${API_BASE_URL}/clarity/next-step`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // Authorization header will be handled by an interceptor or context
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to get next step suggestion');
  }

  return response.json();
}
