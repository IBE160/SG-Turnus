
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SummarizePage from '../page';
import * as studyMaterialService from '../../../services/studyMaterialService';

jest.mock('../../../services/studyMaterialService');

describe('SummarizePage', () => {
  const mockSummarizeText = studyMaterialService.summarizeText as jest.Mock;
  const mockExportSummary = studyMaterialService.exportSummary as jest.Mock;

  beforeEach(() => {
    mockSummarizeText.mockClear();
    mockExportSummary.mockClear();
  });

  it('should render the page with the title', () => {
    render(<SummarizePage />);
    const heading = screen.getByRole('heading', { level: 1, name: 'AI Text Summarizer' });
    expect(heading).toBeInTheDocument();
  });

  it('should not show the export button initially', () => {
    render(<SummarizePage />);
    const exportButton = screen.queryByRole('button', { name: /export summary/i });
    expect(exportButton).not.toBeInTheDocument();
  });

  it('should show the export button and format selector after generating a summary', async () => {
    render(<SummarizePage />);
    mockSummarizeText.mockResolvedValue({ summary: 'This is a summary.' });

    const textarea = screen.getByPlaceholderText(/paste your content here/i);
    fireEvent.change(textarea, { target: { value: 'This is a long text to summarize.' } });

    const summarizeButton = screen.getByRole('button', { name: /generate summary/i });
    fireEvent.click(summarizeButton);

    await waitFor(() => {
      expect(screen.getByText('This is a summary.')).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export summary/i });
    expect(exportButton).toBeInTheDocument();

    const formatSelector = screen.getByLabelText('Export format');
    expect(formatSelector).toBeInTheDocument();
  });

  it('should call exportSummary with the correct parameters when export button is clicked', async () => {
    render(<SummarizePage />);
    const summaryText = 'This is a summary.';
    mockSummarizeText.mockResolvedValue({ summary: summaryText });
    mockExportSummary.mockResolvedValue(new Blob());

    const textarea = screen.getByPlaceholderText(/paste your content here/i);
    fireEvent.change(textarea, { target: { value: 'This is a long text to summarize.' } });

    const summarizeButton = screen.getByRole('button', { name: /generate summary/i });
    fireEvent.click(summarizeButton);

    await waitFor(() => {
      expect(screen.getByText(summaryText)).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export summary/i });
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(mockExportSummary).toHaveBeenCalledWith({
        content: summaryText,
        format: 'pdf',
      });
    });

    const formatSelector = screen.getByLabelText('Export format');
    fireEvent.change(formatSelector, { target: { value: 'docx' } });

    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(mockExportSummary).toHaveBeenCalledWith({
        content: summaryText,
        format: 'docx',
      });
    });
  });
});
