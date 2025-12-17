// the-ai-helping-tool/services/__tests__/studyMaterialService.test.ts

import {
  getStudyMaterials,
  createStudyMaterial,
  updateStudyMaterial,
  getUpdatedStudyMaterials,
  StudyMaterialResponse,
  StudyMaterialUpdate,
} from '../studyMaterialService';

const API_BASE_URL = '/api/v1';

describe('studyMaterialService', () => {
  beforeEach(() => {
    // Reset mocks before each test
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('getStudyMaterials', () => {
    it('should fetch study materials successfully', async () => {
      const mockMaterials: StudyMaterialResponse[] = [
        {
          id: 1,
          user_id: 1,
          file_name: 'test1.pdf',
          s3_key: 's3/test1.pdf',
          upload_date: new Date().toISOString(),
          processing_status: 'completed',
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockMaterials,
      });

      const materials = await getStudyMaterials();
      expect(materials).toEqual(mockMaterials);
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/study-materials`, {
        method: 'GET',
      });
    });

    it('should throw an error if fetching study materials fails', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Network error' }),
      });

      await expect(getStudyMaterials()).rejects.toThrow('Network error');
    });
  });

  describe('createStudyMaterial', () => {
    it('should create a study material successfully', async () => {
      const mockFile = new File(['test content'], 'new-doc.txt', { type: 'text/plain' });
      const mockFileName = 'new-doc.txt';
      const mockResponse: StudyMaterialResponse = {
        id: 2,
        user_id: 1,
        file_name: mockFileName,
        s3_key: 's3/new-doc.txt',
        upload_date: new Date().toISOString(),
        processing_status: 'pending',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const material = await createStudyMaterial(mockFile, mockFileName);
      expect(material).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/study-materials`, {
        method: 'POST',
        body: expect.any(FormData), // Expect FormData
      });

      const callBody = (global.fetch as jest.Mock).mock.calls[0][1].body;
      expect(callBody.get('file').name).toBe(mockFileName);
    });

    it('should throw an error if creating a study material fails', async () => {
      const mockFile = new File(['test content'], 'new-doc.txt', { type: 'text/plain' });
      const mockFileName = 'new-doc.txt';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Upload failed' }),
      });

      await expect(createStudyMaterial(mockFile, mockFileName)).rejects.toThrow('Upload failed');
    });
  });

  describe('updateStudyMaterial', () => {
    it('should update a study material successfully', async () => {
      const materialId = 1;
      const updateData: StudyMaterialUpdate = { file_name: 'updated-name.pdf' };
      const mockResponse: StudyMaterialResponse = {
        id: materialId,
        user_id: 1,
        file_name: 'updated-name.pdf',
        s3_key: 's3/old-name.pdf',
        upload_date: new Date().toISOString(),
        processing_status: 'completed',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const material = await updateStudyMaterial(materialId, updateData);
      expect(material).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/study-materials/${materialId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
    });

    it('should throw an error if updating a study material fails', async () => {
      const materialId = 1;
      const updateData: StudyMaterialUpdate = { file_name: 'updated-name.pdf' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Update failed' }),
      });

      await expect(updateStudyMaterial(materialId, updateData)).rejects.toThrow('Update failed');
    });
  });

  describe('getUpdatedStudyMaterials', () => {
    it('should fetch updated study materials successfully', async () => {
      const sinceTimestamp = new Date().toISOString();
      const mockUpdatedMaterials: StudyMaterialResponse[] = [
        {
          id: 3,
          user_id: 1,
          file_name: 'updated.txt',
          s3_key: 's3/updated.txt',
          upload_date: sinceTimestamp,
          processing_status: 'completed',
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUpdatedMaterials,
      });

      const materials = await getUpdatedStudyMaterials(sinceTimestamp);
      expect(materials).toEqual(mockUpdatedMaterials);
      expect(global.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/study-materials/updates?since=${sinceTimestamp}`, {
        method: 'GET',
      });
    });

    it('should throw an error if fetching updated study materials fails', async () => {
      const sinceTimestamp = new Date().toISOString();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Polling error' }),
      });

      await expect(getUpdatedStudyMaterials(sinceTimestamp)).rejects.toThrow('Polling error');
    });
  });
});
