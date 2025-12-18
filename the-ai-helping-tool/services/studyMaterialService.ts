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
 * @param data The SummarizeRequest object containing the text and optional detail level.
 * @returns A promise that resolves to the SummarizeResponse.
 */
export async function summarizeText(data: SummarizeRequest): Promise<SummarizeResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/summarize`, {
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
 * @param data The FlashcardGenerateRequest object containing the text.
 * @returns A promise that resolves to the FlashcardGenerateResponse.
 */
export async function generateFlashcards(data: FlashcardGenerateRequest): Promise<FlashcardGenerateResponse> {
  const response = await fetch(`${API_BASE_URL}/study-materials/flashcards`, {
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
