// the-ai-helping-tool/app/dashboard/__tests__/page.test.tsx

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../page';
import * as studyMaterialService from '@/services/studyMaterialService';
import * as authService from '@/services/authService';
import * as clarityService from '@/services/clarityService'; // Import clarityService
import { useRouter } from 'next/navigation';
import { NextStep, AIModule, InteractionPatternType } from '@/services/clarityService'; // Import NextStep interface

// Mock the useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the authService
jest.mock('@/services/authService', () => ({
  logoutUser: jest.fn(),
}));

// Mock the studyMaterialService
jest.mock('@/services/studyMaterialService', () => ({
  getStudyMaterials: jest.fn(),
  createStudyMaterial: jest.fn(),
  updateStudyMaterial: jest.fn(),
  getUpdatedStudyMaterials: jest.fn(),
}));

// Mock the clarityService
jest.mock('@/services/clarityService', () => ({
  getNextStepSuggestion: jest.fn(),
}));

describe('DashboardPage', () => {
  const mockPush = jest.fn();
  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    jest.clearAllMocks();
    jest.useFakeTimers(); // Enable fake timers for polling test
  });

  afterEach(() => {
    jest.runOnlyPendingTimers(); // Run any pending timers
    jest.useRealTimers(); // Restore real timers
  });


  it('renders loading state initially', () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockReturnValueOnce(new Promise(() => {})); // Never resolve
    render(<DashboardPage />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders study materials after fetching', async () => {
    const mockMaterials = [
      { id: 1, file_name: 'Doc1.pdf', upload_date: new Date().toISOString(), processing_status: 'completed' },
      { id: 2, file_name: 'Doc2.txt', upload_date: new Date().toISOString(), processing_status: 'pending' },
    ];
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce(mockMaterials);

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Doc1.pdf')).toBeInTheDocument();
      expect(screen.getByText('Doc2.txt')).toBeInTheDocument();
    });
  });

  it('renders error message if fetching study materials fails', async () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockRejectedValueOnce(new Error('Failed to fetch'));

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Failed to fetch');
    });
  });

  it('allows uploading a new study material', async () => {
    const mockMaterials: any[] = [];
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce(mockMaterials);

    const mockFile = new File(['test content'], 'upload.pdf', { type: 'application/pdf' });
    const mockResponse = { id: 3, file_name: 'upload.pdf', upload_date: new Date().toISOString(), processing_status: 'pending' };
    (studyMaterialService.createStudyMaterial as jest.Mock).mockResolvedValueOnce(mockResponse);

    render(<DashboardPage />);

    // Wait for initial fetch to complete
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());

    const fileInput = screen.getByLabelText(/upload new study material/i).closest('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    const uploadButton = screen.getByRole('button', { name: /upload material/i });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(studyMaterialService.createStudyMaterial).toHaveBeenCalledWith(mockFile, mockFile.name);
      expect(screen.getByText('File uploaded successfully!')).toBeInTheDocument();
      expect(screen.getByText('upload.pdf')).toBeInTheDocument();
    });
  });

  it('handles upload error', async () => {
    const mockMaterials: any[] = [];
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce(mockMaterials);
    const mockFile = new File(['test content'], 'bad-upload.pdf', { type: 'application/pdf' });
    (studyMaterialService.createStudyMaterial as jest.Mock).mockRejectedValueOnce(new Error('Upload failed'));

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());


    const fileInput = screen.getByLabelText(/upload new study material/i).closest('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    const uploadButton = screen.getByRole('button', { name: /upload material/i });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Upload failed');
    });
  });

  it('allows editing a study material name', async () => {
    const mockMaterials = [
      { id: 1, file_name: 'OldName.pdf', upload_date: new Date().toISOString(), processing_status: 'completed' },
    ];
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce(mockMaterials);
    const mockUpdatedMaterial = { ...mockMaterials[0], file_name: 'NewName.pdf' };
    (studyMaterialService.updateStudyMaterial as jest.Mock).mockResolvedValueOnce(mockUpdatedMaterial);

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('OldName.pdf')).toBeInTheDocument());

    fireEvent.click(screen.getByLabelText('edit')); // Click edit icon

    const textField = screen.getByDisplayValue('OldName.pdf');
    fireEvent.change(textField, { target: { value: 'NewName.pdf' } });

    fireEvent.click(screen.getByLabelText('save')); // Click save icon

    await waitFor(() => {
      expect(studyMaterialService.updateStudyMaterial).toHaveBeenCalledWith(1, { file_name: 'NewName.pdf' });
      expect(screen.getByText('NewName.pdf')).toBeInTheDocument();
    });
  });

  it('polls for updated study materials', async () => {
    const initialMaterials = [
      { id: 1, file_name: 'Initial.pdf', upload_date: new Date('2023-01-01T00:00:00.000Z').toISOString(), processing_status: 'completed' },
    ];
    const updatedMaterials = [
      { id: 2, file_name: 'NewPolled.pdf', upload_date: new Date().toISOString(), processing_status: 'pending' },
    ];
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce(initialMaterials);
    (studyMaterialService.getUpdatedStudyMaterials as jest.Mock).mockResolvedValueOnce(updatedMaterials);

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('Initial.pdf')).toBeInTheDocument());

    jest.advanceTimersByTime(5000); // Advance timers by POLLING_INTERVAL

    await waitFor(() => {
      expect(studyMaterialService.getUpdatedStudyMaterials).toHaveBeenCalledTimes(1);
      expect(screen.getByText('NewPolled.pdf')).toBeInTheDocument();
    });
  });

  it('calls logoutUser and redirects to login on logout button click', async () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce([]); // Resolve immediately for setup
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /logout/i }));

    expect(authService.logoutUser).toHaveBeenCalledTimes(1);
    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  // New tests for Next Step Suggestion functionality
  it('displays next step suggestion after query', async () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce([]);
    const mockNextStepResponse: NextStep = {
      ai_module: AIModule.QA,
      interaction_pattern: InteractionPatternType.ANCHOR_QUESTION,
      parameters: {},
    };
    (clarityService.getNextStepSuggestion as jest.Mock).mockResolvedValueOnce(mockNextStepResponse);

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());

    const queryInput = screen.getByLabelText('Your Query');
    fireEvent.change(queryInput, { target: { value: 'What is photosynthesis?' } });

    const getSuggestionButton = screen.getByRole('button', { name: /get suggestion/i });
    fireEvent.click(getSuggestionButton);

    await waitFor(() => {
      expect(clarityService.getNextStepSuggestion).toHaveBeenCalledWith({ text: 'What is photosynthesis?' });
      expect(screen.getByText('Suggested Next Step:')).toBeInTheDocument();
      expect(screen.getByText('AI Module: QAModule')).toBeInTheDocument();
      expect(screen.getByText('Interaction Pattern: anchor_question')).toBeInTheDocument();
    });
  });

  it('shows loading state for next step suggestion', async () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce([]);
    (clarityService.getNextStepSuggestion as jest.Mock).mockReturnValueOnce(new Promise(() => {})); // Never resolve

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());

    const queryInput = screen.getByLabelText('Your Query');
    fireEvent.change(queryInput, { target: { value: 'test query' } });

    const getSuggestionButton = screen.getByRole('button', { name: /get suggestion/i });
    fireEvent.click(getSuggestionButton);

    await waitFor(() => {
      expect(getSuggestionButton).toBeDisabled();
      expect(queryInput).toBeDisabled();
      expect(screen.getAllByRole('progressbar').length).toBeGreaterThanOrEqual(1); // At least one progressbar (upload/next-step)
    });
  });

  it('displays error message for next step suggestion failure', async () => {
    (studyMaterialService.getStudyMaterials as jest.Mock).mockResolvedValueOnce([]);
    (clarityService.getNextStepSuggestion as jest.Mock).mockRejectedValueOnce(new Error('Failed to get suggestion'));

    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByText('No study materials found. Upload one to get started!')).toBeInTheDocument());

    const queryInput = screen.getByLabelText('Your Query');
    fireEvent.change(queryInput, { target: { value: 'error query' } });

    const getSuggestionButton = screen.getByRole('button', { name: /get suggestion/i });
    fireEvent.click(getSuggestionButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Failed to get suggestion');
    });
  });
});

