// the-ai-helping-tool/services/__tests__/studyMaterialService.test.ts
import { summarizeText, generateFlashcards } from '../studyMaterialService'; // Import generateFlashcards

// Mock the global fetch API
global.fetch = jest.fn();

describe('studyMaterialService', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    jest.restoreAllMocks();
  });

  describe('summarizeText', () => {
    it('should successfully generate a normal summary', async () => {
      const mockSummary = { summary: 'This is a mocked summary.' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSummary,
      });

      const requestPayload = {
        text: 'A long article about something interesting.',
        detail_level: 'normal',
      };
      const result = await summarizeText(requestPayload);

      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith('/api/v1/study-materials/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      expect(result).toEqual(mockSummary);
    });

    it('should successfully generate a brief summary', async () => {
      const mockSummary = { summary: 'Brief mocked summary.' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSummary,
      });

      const requestPayload = {
        text: 'A very very long text that needs to be briefly summarized.',
        detail_level: 'brief',
      };
      const result = await summarizeText(requestPayload);

      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith('/api/v1/study-materials/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      expect(result).toEqual(mockSummary);
    });

    it('should throw an error if API call fails', async () => {
      const mockError = { detail: 'Summarization failed.' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => mockError,
      });

      const requestPayload = {
        text: 'Text that will cause an error.',
      };

      await expect(summarizeText(requestPayload)).rejects.toThrow('Summarization failed.');
      expect(fetch).toHaveBeenCalledTimes(1);
    });

    it('should throw a generic error if API call fails without specific detail', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}), // Empty error response
      });

      const requestPayload = {
        text: 'Text that will cause a generic error.',
      };

      await expect(summarizeText(requestPayload)).rejects.toThrow('Failed to generate summary');
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('generateFlashcards', () => {
    it('should successfully generate flashcards', async () => {
      const mockFlashcards = {
        flashcards: [
          { question: 'Q1', answer: 'A1' },
          { question: 'Q2', answer: 'A2' },
        ],
      };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockFlashcards,
      });

      const requestPayload = {
        text: 'Text to generate flashcards from.',
      };
      const result = await generateFlashcards(requestPayload);

      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith('/api/v1/study-materials/flashcards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });
      expect(result).toEqual(mockFlashcards);
    });

    it('should throw an error if flashcard API call fails', async () => {
      const mockError = { detail: 'Flashcard generation failed.' };
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => mockError,
      });

      const requestPayload = {
        text: 'Text that will cause a flashcard error.',
      };

      await expect(generateFlashcards(requestPayload)).rejects.toThrow('Flashcard generation failed.');
      expect(fetch).toHaveBeenCalledTimes(1);
    });

    it('should throw a generic error if flashcard API call fails without specific detail', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}), // Empty error response
      });

      const requestPayload = {
        text: 'Text that will cause a generic flashcard error.',
      };

      await expect(generateFlashcards(requestPayload)).rejects.toThrow('Failed to generate flashcards');
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });
});