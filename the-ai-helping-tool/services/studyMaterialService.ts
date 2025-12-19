// the-ai-helping-tool/services/studyMaterialService.ts

import axios from 'axios'; // Import axios for consistent request handling

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'; // Use environment variable

// --- TypeScript Interfaces (Mirroring Backend Pydantic Schemas) ---
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

export interface StudyMaterialResponse {
  id: number;
  user_id: number;
  file_name: string;
  s3_key: string;
  upload_date: string; // ISO 8601 string
  processing_status: string;
  generated_summaries: GeneratedSummaryResponse[]; // Added for eager loading
  generated_flashcard_sets: GeneratedFlashcardSetResponse[]; // Added for eager loading
  generated_quizzes: GeneratedQuizResponse[]; // Added for eager loading
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


// --- API Service Functions ---

/**
 * Creates a new study material by uploading a file.
 * @param file The file to upload.
 * @param token The authentication token.
 * @returns A promise that resolves to the created StudyMaterialResponse.
 */
export async function createStudyMaterial(file: File, token: string): Promise<StudyMaterialResponse> {
  const formData = new FormData();
  formData.append('file', file); // No need for fileName parameter, as it's part of File object

  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/study-materials`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error creating study material:', error);
    throw error;
  }
}

/**
 * Retrieves a list of all study materials for the current user.
 * @param token The authentication token.
 * @returns A promise that resolves to an array of StudyMaterialResponse.
 */
export async function getStudyMaterials(token: string): Promise<StudyMaterialResponse[]> {
  console.log('Returning mock study materials');
  return Promise.resolve([
    {
      id: 1,
      user_id: 1,
      file_name: 'My Awesome Study Notes.pdf',
      s3_key: 'dummy-key',
      upload_date: new Date().toISOString(),
      processing_status: 'processed',
      generated_summaries: [
        {
          id: 1,
          study_material_id: 1,
          content: 'This is a summary of the study notes.',
          detail_level: 'medium',
          generated_at: new Date().toISOString(),
        },
      ],
      generated_flashcard_sets: [
        {
          id: 1,
          study_material_id: 1,
          content: [
            { question: 'What is the capital of France?', answer: 'Paris' },
            { question: 'What is 2 + 2?', answer: '4' },
          ],
          generated_at: new Date().toISOString(),
        },
      ],
      generated_quizzes: [
        {
          id: 1,
          study_material_id: 1,
          content: [
            {
              question: 'What is the capital of France?',
              options: ['London', 'Paris', 'Berlin', 'Madrid'],
              correct_answer: 'Paris',
            },
          ],
          generated_at: new Date().toISOString(),
        },
      ],
    },
  ]);
}

/**
 * Retrieves a single study material by its ID.
 * @param id The ID of the study material.
 * @param token The authentication token.
 * @returns A promise that resolves to the StudyMaterialResponse.
 */
export async function getStudyMaterial(id: number, token: string): Promise<StudyMaterialResponse> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/study-materials/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching study material with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Updates the metadata of an existing study material.
 * @param id The ID of the study material to update.
 * @param data The partial data to update.
 * @param token The authentication token.
 * @returns A promise that resolves to the updated StudyMaterialResponse.
 */
export async function updateStudyMaterial(id: number, data: StudyMaterialUpdate, token: string): Promise<StudyMaterialResponse> {
  try {
    const response = await axios.put(`${API_BASE_URL}/api/v1/study-materials/${id}`, data, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error updating study material with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Deletes a study material by its ID.
 * @param id The ID of the study material to delete.
 * @param token The authentication token.
 * @returns A promise that resolves when the deletion is successful.
 */
export async function deleteStudyMaterial(id: number, token: string): Promise<void> {
  try {
    await axios.delete(`${API_BASE_URL}/api/v1/study-materials/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error(`Error deleting study material with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Retrieves study materials that have been updated since a given timestamp.
 * @param since A timestamp (ISO 8601 string) to fetch updates from.
 * @param token The authentication token.
 * @returns A promise that resolves to an array of StudyMaterialResponse.
 */
export async function getUpdatedStudyMaterials(since: string, token: string): Promise<StudyMaterialResponse[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/study-materials/updates?since=${since}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching updated study materials:', error);
    throw error;
  }
}

/**
 * Generates a summary for the provided text.
 * @param studyMaterialId The ID of the study material to associate the summary with.
 * @param data The SummarizeRequest object containing the text and optional detail level.
 * @param token The authentication token.
 * @returns A promise that resolves to the GeneratedSummaryResponse.
 */
export async function summarizeText(
  studyMaterialId: number,
  data: SummarizeRequest,
  token: string
): Promise<GeneratedSummaryResponse> {
  console.log('Returning mock summary');
  const summaryContent = `This is a mock summary for the provided text. Detail level: ${data.detail_level}.`;
  return Promise.resolve({
    id: Math.floor(Math.random() * 1000),
    study_material_id: studyMaterialId,
    content: summaryContent,
    detail_level: data.detail_level,
    generated_at: new Date().toISOString(),
  });
}

/**
 * Generates flashcards for the provided text.
 * @param studyMaterialId The ID of the study material to associate the flashcards with.
 * @param data The FlashcardGenerateRequest object containing the text.
 * @param token The authentication token.
 * @returns A promise that resolves to the GeneratedFlashcardSetResponse.
 */
export async function generateFlashcards(
  studyMaterialId: number,
  data: FlashcardGenerateRequest,
  token: string
): Promise<GeneratedFlashcardSetResponse> {
  console.log('Returning mock flashcards');
  const flashcards: GeneratedFlashcardResponse[] = [
    { question: 'What is the capital of Mockland?', answer: 'Mockville' },
    { question: 'What is the main export of Mockland?', answer: 'Mock data' },
  ];
  return Promise.resolve({
    id: Math.floor(Math.random() * 1000),
    study_material_id: studyMaterialId,
    content: flashcards,
    generated_at: new Date().toISOString(),
  });
}

/**
 * Generates a quiz for the provided text.
 * @param studyMaterialId The ID of the study material to associate the quiz with.
 * @param data The QuizGenerateRequest object containing the text.
 * @param token The authentication token.
 * @returns A promise that resolves to the GeneratedQuizResponse.
 */
export async function generateQuiz(
  studyMaterialId: number,
  data: QuizGenerateRequest,
  token: string
): Promise<GeneratedQuizResponse> {
  console.log('Returning mock quiz');
  const questions: GeneratedQuizQuestionResponse[] = [
    {
      question: 'What is the capital of Mockland?',
      options: ['Mockville', 'Testburg', 'Faketon', 'Datapolis'],
      correct_answer: 'Mockville',
    },
    {
      question: 'What is the main export of Mockland?',
      options: ['Mock data', 'Real data', 'Spam', 'Gold'],
      correct_answer: 'Mock data',
    },
  ];
  return Promise.resolve({
    id: Math.floor(Math.random() * 1000),
    study_material_id: studyMaterialId,
    content: questions,
    generated_at: new Date().toISOString(),
  });
}

export interface ExportRequest {
  content: string;
  format: string;
}

/**
 * Exports a summary in a specified format.
 * @param data The ExportRequest object containing the content and format.
 * @returns A promise that resolves to a Blob.
 */
export async function exportSummary(data: ExportRequest): Promise<Blob> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/study-materials/export`,
      data,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error exporting summary:', error);
    throw error;
  }
}

/**
 * Retrieves a list of generated summaries for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @param token The authentication token.
 * @returns A promise that resolves to an array of GeneratedSummaryResponse.
 */
export async function getSummariesForStudyMaterial(studyMaterialId: number, token: string): Promise<GeneratedSummaryResponse[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/study-materials/${studyMaterialId}/summaries`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching summaries for study material ${studyMaterialId}:`, error);
    throw error;
  }
}

/**
 * Retrieves a list of generated flashcard sets for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @param token The authentication token.
 * @returns A promise that resolves to an array of GeneratedFlashcardSetResponse.
 */
export async function getFlashcardSetsForStudyMaterial(studyMaterialId: number, token: string): Promise<GeneratedFlashcardSetResponse[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/study-materials/${studyMaterialId}/flashcard-sets`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching flashcard sets for study material ${studyMaterialId}:`, error);
    throw error;
  }
}

/**
 * Retrieves a list of generated quizzes for a specific study material.
 * @param studyMaterialId The ID of the study material.
 * @param token The authentication token.
 * @returns A promise that resolves to an array of GeneratedQuizResponse.
 */
export async function getQuizzesForStudyMaterial(studyMaterialId: number, token: string): Promise<GeneratedQuizResponse[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/study-materials/${studyMaterialId}/quizzes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching quizzes for study material ${studyMaterialId}:`, error);
    throw error;
  }
}

/**
 * Exports a generated study material in a specified format.
 * @param materialType The type of material to export (e.g., "summary", "flashcard_set", "quiz").
 * @param materialId The ID of the generated material.
 * @param format The desired export format (e.g., "pdf", "docx", "csv").
 * @param token The authentication token.
 * @returns A promise that resolves when the file is downloaded.
 */
export async function exportGeneratedMaterial(
  materialType: string,
  materialId: number,
  format: string,
  token: string
): Promise<void> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/v1/export/${materialType}/${materialId}?format=${format}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      responseType: 'blob', // Important for downloading files
    });

    // Get the filename from the Content-Disposition header
    const contentDisposition = response.headers['content-disposition'];
    let filename = `exported_material.${format}`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }

    // Create a blob from the response and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error(`Error exporting ${materialType} with ID ${materialId}:`, error);
    throw error;
  }
}