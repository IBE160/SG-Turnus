// the-ai-helping-tool/components/StudyMaterialList.test.tsx
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StudyMaterialList from './StudyMaterialList';
import * as studyMaterialService from '../services/studyMaterialService'; // Import the service to mock it

// Mock the entire studyMaterialService module
jest.mock('../services/studyMaterialService', () => ({
  ...jest.requireActual('../services/studyMaterialService'), // Use actual for non-mocked parts
  getStudyMaterials: jest.fn(),
  getUpdatedStudyMaterials: jest.fn(),
  updateStudyMaterial: jest.fn(),
}));

const mockGetStudyMaterials = studyMaterialService.getStudyMaterials as jest.Mock;
const mockGetUpdatedStudyMaterials = studyMaterialService.getUpdatedStudyMaterials as jest.Mock;
const mockUpdateStudyMaterial = studyMaterialService.updateStudyMaterial as jest.Mock;

describe('StudyMaterialList', () => {
  beforeEach(() => {
    jest.useFakeTimers(); // Control timers for polling tests
    mockGetStudyMaterials.mockReset();
    mockGetUpdatedStudyMaterials.mockReset();
    mockUpdateStudyMaterial.mockReset();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers(); // Clear any remaining timers
    jest.useRealTimers(); // Restore real timers
  });

  test('renders loading state initially', () => {
    mockGetStudyMaterials.mockReturnValueOnce(new Promise(() => {})); // Never resolve to keep it in loading
    render(<StudyMaterialList />);
    expect(screen.getByText(/Loading study materials.../i)).toBeInTheDocument();
  });

  test('renders error state if initial fetch fails', async () => {
    mockGetStudyMaterials.mockRejectedValueOnce(new Error('Network error'));
    render(<StudyMaterialList />);
    await waitFor(() => expect(screen.getByText(/Error: Failed to fetch initial study materials: Network error/i)).toBeInTheDocument());
  });

  test('renders no materials message if no materials are present', async () => {
    mockGetStudyMaterials.mockResolvedValueOnce([]);
    render(<StudyMaterialList />);
    await waitFor(() => expect(screen.getByText(/No study materials uploaded yet./i)).toBeInTheDocument());
  });

  test('renders a list of study materials', async () => {
    const materials = [
      { id: 1, user_id: 1, file_name: 'Doc1.pdf', s3_key: 'key1', upload_date: new Date().toISOString(), processing_status: 'pending', updated_at: new Date().toISOString() },
      { id: 2, user_id: 1, file_name: 'Doc2.txt', s3_key: 'key2', upload_date: new Date().toISOString(), processing_status: 'complete', updated_at: new Date().toISOString() },
    ];
    mockGetStudyMaterials.mockResolvedValueOnce(materials);

    render(<StudyMaterialList />);
    await waitFor(() => expect(screen.getByText(/Doc1.pdf/i)).toBeInTheDocument());
    expect(screen.getByText(/Doc2.txt/i)).toBeInTheDocument();
  });

  test('polls for updates and updates the list', async () => {
    const initialMaterials = [
      { id: 1, user_id: 1, file_name: 'Doc1.pdf', s3_key: 'key1', upload_date: new Date().toISOString(), processing_status: 'pending', updated_at: new Date().toISOString() },
    ];
    const updatedMaterial = { id: 1, user_id: 1, file_name: 'Doc1.pdf', s3_key: 'key1', upload_date: new Date().toISOString(), processing_status: 'complete', updated_at: new Date(Date.now() + 1000).toISOString() };
    const newMaterial = { id: 3, user_id: 1, file_name: 'Doc3.pptx', s3_key: 'key3', upload_date: new Date().toISOString(), processing_status: 'pending', updated_at: new Date(Date.now() + 2000).toISOString() };

    mockGetStudyMaterials.mockResolvedValueOnce(initialMaterials);
    mockGetUpdatedStudyMaterials.mockResolvedValueOnce([updatedMaterial, newMaterial]);

    render(<StudyMaterialList />);

    // Wait for initial render
    await waitFor(() => expect(screen.getByText(/Doc1.pdf/i)).toBeInTheDocument());
    expect(screen.getByText(/Status: pending/i)).toBeInTheDocument();

    // Advance timers to trigger polling
    await act(async () => {
      jest.advanceTimersByTime(5000); // Advance by polling interval
    });
    
    // Check if the list is updated
    await waitFor(() => expect(screen.getByText(/Status: complete/i)).toBeInTheDocument());
    expect(screen.getByText(/Doc3.pptx/i)).toBeInTheDocument();
  });

  test('updates a study material when "Mark Processing" is clicked', async () => {
    const initialMaterials = [
      { id: 1, user_id: 1, file_name: 'Doc1.pdf', s3_key: 'key1', upload_date: new Date().toISOString(), processing_status: 'pending', updated_at: new Date().toISOString() },
    ];
    const updatedMaterial = { ...initialMaterials[0], processing_status: 'processing', updated_at: new Date(Date.now() + 1000).toISOString() };

    mockGetStudyMaterials.mockResolvedValueOnce(initialMaterials);
    mockUpdateStudyMaterial.mockResolvedValueOnce(updatedMaterial);
    mockGetUpdatedStudyMaterials.mockResolvedValue([]); // Prevent polling from interfering with this test's update

    render(<StudyMaterialList />);

    await waitFor(() => expect(screen.getByText(/Doc1.pdf/i)).toBeInTheDocument());
    const markProcessingButton = screen.getByRole('button', { name: /Mark Processing/i });
    
    act(() => {
      userEvent.click(markProcessingButton);
    });

    await waitFor(() => expect(mockUpdateStudyMaterial).toHaveBeenCalledWith(1, { processing_status: 'processing' }));
    await waitFor(() => expect(screen.getByText(/Status: processing/i)).toBeInTheDocument());
  });

  test('updates a study material when "Rename" is clicked', async () => {
    const initialMaterials = [
      { id: 1, user_id: 1, file_name: 'OldName.pdf', s3_key: 'key1', upload_date: new Date().toISOString(), processing_status: 'pending', updated_at: new Date().toISOString() },
    ];
    const updatedMaterial = { ...initialMaterials[0], file_name: 'OldName.pdf (renamed)', updated_at: new Date(Date.now() + 1000).toISOString() };

    mockGetStudyMaterials.mockResolvedValueOnce(initialMaterials);
    mockUpdateStudyMaterial.mockResolvedValueOnce(updatedMaterial);
    mockGetUpdatedStudyMaterials.mockResolvedValue([]); // Prevent polling from interfering

    render(<StudyMaterialList />);

    await waitFor(() => expect(screen.getByText(/OldName.pdf/i)).toBeInTheDocument());
    const renameButton = screen.getByRole('button', { name: /Rename/i });
    
    act(() => {
      userEvent.click(renameButton);
    });

    await waitFor(() => expect(mockUpdateStudyMaterial).toHaveBeenCalledWith(1, { file_name: 'OldName.pdf (renamed)' }));
    await waitFor(() => expect(screen.getByText(/OldName.pdf \(renamed\)/i)).toBeInTheDocument());
  });
});
