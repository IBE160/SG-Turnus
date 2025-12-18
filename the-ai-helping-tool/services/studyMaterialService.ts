// the-ai-helping-tool/services/studyMaterialService.ts

// --- TypeScript Interfaces (Mirroring Backend Pydantic Schemas) ---
export interface StudyMaterialResponse {
  id: number;
  user_id: number;
  file_name: string;
  s3_key: string;
  upload_date: string; // ISO 8601 string
  processing_status: string;
}

export interface StudyMaterialUpdate {
  file_name?: string;
  processing_status?: string;
}

export interface SummarizeRequest {
  text: string;
  detail_level?: string;
}

export interface SummarizeResponse {
  summary: string;
}

export interface Flashcard {
  question: string;
  answer: string;
}

export interface FlashcardGenerateRequest {
  text: string;
}

export interface FlashcardGenerateResponse {
  flashcards: Flashcard[];
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
}

export interface QuizGenerateRequest {
  text: string;
}

export interface QuizGenerateResponse {
  questions: QuizQuestion[];
}

export interface GeneratedSummaryResponse {
  id: number;
  study_material_id: number;
  content: string;
  detail_level?: string;
  generated_at: string;
}

export interface GeneratedFlashcardResponse {
  question: string;
  answer: string;
}

export interface GeneratedFlashcardSetResponse {
  id: number;
  study_material_id: number;
  content: GeneratedFlashcardResponse[];
  generated_at: string;
}

export interface GeneratedQuizQuestionResponse {
  question: string;
  options: string[];
  correct_answer: string;
}

export interface GeneratedQuizResponse {
  id: number;
  study_material_id: number;
  content: GeneratedQuizQuestionResponse[];
  generated_at: string;
}


// --- API Service Functions ---
const API_BASE_URL = '/api/v1'; // Assuming a proxy or direct access to backend

/**
 * Creates a new study material by uploading a file.
 * @param file The file to upload.
 * @param fileName The name of the file.
 * @returns A promise that resolves to the created StudyMaterialResponse.
 */
export async function createStudyMaterial(file: File, fileName: string): Promise<StudyMaterialResponse> {
  const formData = new FormData();
  formData.append('file', file, fileName);

  const response = await fetch(`${API_BASE_URL}/study-materials`, {
    method: 'POST',
    body: formData,
    // Headers like Authorization will be handled by an interceptor or passed from context
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create study material');
  }

  return response.json();
}

/**
 * Retrieves a list of all study materials for the current user.
 * @returns A promise that resolves to an array of StudyMaterialResponse.
 */
export async function getStudyMaterials(): Promise<StudyMaterialResponse[]> {
  const response = await fetch(`${API_BASE_URL}/study-materials`, {
    method: 'GET',
    // Headers like Authorization will be handled by an interceptor or passed from context
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch study materials');
  }

  return response.json();
}

/**
 * Retrieves a single study material by its ID.
 * @param id The ID of the study material.
 * @returns A promise that resolves to the StudyMaterialResponse.
 */
export async function getStudyMaterial(id: number): Promise<StudyMaterialResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${id}`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to fetch study material with ID ${id}`);
  }

  return response.json();
}

/**
 * Updates the metadata of an existing study material.
 * @param id The ID of the study material to update.
 * @param data The partial data to update.
 * @returns A promise that resolves to the updated StudyMaterialResponse.
 */
export async function updateStudyMaterial(id: number, data: StudyMaterialUpdate): Promise<StudyMaterialResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      // Headers like Authorization will be handled by an interceptor or passed from context
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to update study material with ID ${id}`);
  }

  return response.json();
}

/**
 * Deletes a study material by its ID.
 * @param id The ID of the study material to delete.
 * @returns A promise that resolves when the deletion is successful.
 */
export async function deleteStudyMaterial(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to delete study material with ID ${id}`);
  }
}

/**
 * Retrieves study materials that have been updated since a given timestamp.
 * @param since A timestamp (ISO 8601 string) to fetch updates from.
 * @returns A promise that resolves to an array of StudyMaterialResponse.
 */
export async function getUpdatedStudyMaterials(since: string): Promise<StudyMaterialResponse[]> {
  const response = await fetch(`${API_BASE_URL}/study-materials/updates?since=${since}`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch updated study materials');
  }

  return response.json();
}

/**
 * Generates a summary for the provided text.
 * @param studyMaterialId The ID of the study material to associate the summary with.
 * @param data The SummarizeRequest object containing the text and optional detail level.
 * @returns A promise that resolves to the GeneratedSummaryResponse.
 */
export async function summarizeText(studyMaterialId: number, data: SummarizeRequest): Promise<GeneratedSummaryResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // Authorization header will be handled by an interceptor or passed from context
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to generate summary');
  }

  return response.json();
}

/**
 * Generates flashcards for the provided text.
 * @param studyMaterialId The ID of the study material to associate the flashcards with.
 * @param data The FlashcardGenerateRequest object containing the text.
 * @returns A promise that resolves to the GeneratedFlashcardSetResponse.
 */
export async function generateFlashcards(studyMaterialId: number, data: FlashcardGenerateRequest): Promise<GeneratedFlashcardSetResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/flashcards`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to generate flashcards');
  }

  return response.json();
}

/**
 * Generates a quiz for the provided text.
 * @param studyMaterialId The ID of the study material to associate the quiz with.
 * @param data The QuizGenerateRequest object containing the text.
 * @returns A promise that resolves to the GeneratedQuizResponse.
 */
export async function generateQuiz(studyMaterialId: number, data: QuizGenerateRequest): Promise<GeneratedQuizResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/quiz`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to generate quiz');
  }

  return response.json();
}

/**
 * Retrieves a list of generated summaries for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @returns A promise that resolves to an array of GeneratedSummaryResponse.
 */
export async function getSummariesForStudyMaterial(studyMaterialId: number): Promise<GeneratedSummaryResponse[]> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/summaries`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to fetch summaries for study material ${studyMaterialId}`);
  }

  return response.json();
}

/**
 * Retrieves a list of generated flashcard sets for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @returns A promise that resolves to an array of GeneratedFlashcardSetResponse.
 */
export async function getFlashcardSetsForStudyMaterial(studyMaterialId: number): Promise<GeneratedFlashcardSetResponse[]> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/flashcard-sets`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to fetch flashcard sets for study material ${studyMaterialId}`);
  }

  return response.json();
}

/**
 * Retrieves a list of generated quizzes for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @returns A promise that resolves to an array of GeneratedQuizResponse.
 */
export async function getQuizzesForStudyMaterial(studyMaterialId: number): Promise<GeneratedQuizResponse[]> {
  const response = await fetch(`${API_BASE_URL}/study-materials/${studyMaterialId}/quizzes`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to fetch quizzes for study material ${studyMaterialId}`);
  }

  return response.json();
}

/**
 * Exports a generated study material in a specified format.
 * @param materialType The type of material to export (e.g., "summary", "flashcard_set", "quiz").
 * @param materialId The ID of the generated material.
 * @param format The desired export format (e.g., "pdf", "docx", "csv").
 * @returns A promise that resolves when the file is downloaded.
 */
export async function exportGeneratedMaterial(
  materialType: string,
  materialId: number,
  format: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/export/${materialType}/${materialId}?format=${format}`, {
    method: 'GET',
    // Authorization header will be handled by an interceptor or passed from context
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `Failed to export ${materialType} with ID ${materialId}`);
  }

  // Get the filename from the Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = `exported_material.${format}`;
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }

  // Create a blob from the response and trigger download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}