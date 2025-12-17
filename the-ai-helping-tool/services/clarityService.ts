// the-ai-helping-tool/services/clarityService.ts

const API_BASE_URL = '/api/v1';

// --- TypeScript Interfaces (Mirroring Backend Pydantic Schemas) ---
export interface NLPRequest {
  text: string;
}

export enum NextStep {
  ASK_FOR_CLARIFICATION_QUESTION = "Ask a clarifying question",
  PROVIDE_MICRO_EXPLANATION = "Provide a micro-explanation of the concept",
  SUGGEST_DEFINITION_LOOKUP = "Suggest looking up the definition",

  ASK_FOR_SUMMARY_LENGTH = "Ask for desired summary length",
  GENERATE_BRIEF_SUMMARY = "Generate a brief summary",
  GENERATE_DETAILED_SUMMARY = "Generate a detailed summary",

  BREAK_DOWN_PROBLEM = "Break down the problem into smaller steps",
  SUGGEST_SIMILAR_EXAMPLE = "Suggest a similar example to work through",
  ASK_FOR_USER_ATTEMPT = "Ask the user for their attempt or initial thoughts",

  GENERATE_FLASHCARDS = "Generate flashcards for key concepts",
  CREATE_PRACTICE_QUIZ = "Create a short practice quiz",

  EXPLAIN_CONNECTION = "Explain the connection between concepts",
  ASK_FOR_RELATED_CONCEPTS = "Ask what other concepts the user thinks are related",

  PROVIDE_CORRECT_INFORMATION = "Provide correct information and explain the misconception",
  ASK_FOR_USER_REASONING = "Ask for the user's reasoning behind their statement",

  ASK_OPEN_ENDED_QUESTION = "Ask an open-ended question to gather more context",
  PROVIDE_GENERAL_GUIDANCE = "Provide general guidance on how to approach the topic",
  ACKNOWLEDGE_AND_REPHRASE = "Acknowledge the input and rephrase to confirm understanding",
  NO_CLEAR_NEXT_STEP = "No clear next step, ask user for explicit guidance",
}

export interface ClarityResponse {
  next_step: NextStep;
  explanation: string;
}

// --- API Service Functions ---

/**
 * Fetches the next suggested step from the Clarity AI engine based on user input.
 * @param request The NLPRequest containing the user's text.
 * @returns A promise that resolves to a ClarityResponse.
 */
export async function getNextStepSuggestion(request: NLPRequest): Promise<ClarityResponse> {
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
