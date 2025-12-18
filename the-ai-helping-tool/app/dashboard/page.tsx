// the-ai-helping-tool/app/dashboard/page.tsx
'use client';

import { 
  Typography, Box, Button, TextField, CircularProgress, Alert, Table, TableBody, TableCell, TableHead, TableRow, Paper, TableContainer,
  Menu, MenuItem, IconButton // New imports
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert'; // New import
import { useRouter } from 'next/navigation';
import { logoutUser } from '@/services/authService';
import { getNextStepSuggestion, NextStep } from '@/services/clarityService';
import { useState, useEffect } from 'react';
import { 
  StudyMaterialResponse, 
  getStudyMaterials,
  getSummariesForStudyMaterial, // New import
  getFlashcardSetsForStudyMaterial, // New import
  getQuizzesForStudyMaterial, // New import
  exportGeneratedMaterial, // New import
  GeneratedSummaryResponse, // New import
  GeneratedFlashcardSetResponse, // New import
  GeneratedQuizResponse // New import
} from '@/services/studyMaterialService';

export default function DashboardPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [nextStep, setNextStep] = useState<NextStep | null>(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const [errorSuggestion, setErrorSuggestion] = useState('');

  const [studyMaterials, setStudyMaterials] = useState<StudyMaterialResponse[]>([]);
  const [loadingMaterials, setLoadingMaterials] = useState(true);
  const [errorMaterials, setErrorMaterials] = useState('');

  // State for export menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [currentMaterialId, setCurrentMaterialId] = useState<number | null>(null);
  const [generatedSummaries, setGeneratedSummaries] = useState<GeneratedSummaryResponse[]>([]);
  const [generatedFlashcards, setGeneratedFlashcards] = useState<GeneratedFlashcardSetResponse[]>([]);
  const [generatedQuizzes, setGeneratedQuizzes] = useState<GeneratedQuizResponse[]>([]);
  const [loadingGenerated, setLoadingGenerated] = useState(false);
  const [errorGenerated, setErrorGenerated] = useState('');

  useEffect(() => {
    const fetchStudyMaterials = async () => {
      try {
        const materials = await getStudyMaterials();
        setStudyMaterials(materials);
      } catch (err: any) {
        setErrorMaterials(err.message || 'Failed to fetch study materials.');
      } finally {
        setLoadingMaterials(false);
      }
    };

    fetchStudyMaterials();
  }, []);

  const handleLogout = () => {
    logoutUser();
    router.push('/login'); // Redirect to login page after logout
  };

  const handleGetSuggestion = async () => {
    setLoadingSuggestion(true);
    setErrorSuggestion('');
    setNextStep(null);
    try {
      // Assuming 'query' here is raw text, not linked to a specific study material for clarity generation
      const response = await getNextStepSuggestion({ text: query });
      setNextStep(response);
    } catch (err: any) {
      setErrorSuggestion(err.message || 'An unexpected error occurred.');
    } finally {
      setLoadingSuggestion(false);
    }
  };

  const handleOpenExportMenu = async (event: React.MouseEvent<HTMLElement>, materialId: number) => {
    setAnchorEl(event.currentTarget);
    setCurrentMaterialId(materialId);
    setLoadingGenerated(true);
    setErrorGenerated('');
    setGeneratedSummaries([]);
    setGeneratedFlashcards([]);
    setGeneratedQuizzes([]);

    try {
      const summaries = await getSummariesForStudyMaterial(materialId);
      const flashcards = await getFlashcardSetsForStudyMaterial(materialId);
      const quizzes = await getQuizzesForStudyMaterial(materialId);
      setGeneratedSummaries(summaries);
      setGeneratedFlashcards(flashcards);
      setGeneratedQuizzes(quizzes);
    } catch (err: any) {
      setErrorGenerated(err.message || 'Failed to fetch generated materials.');
    } finally {
      setLoadingGenerated(false);
    }
  };

  const handleCloseExportMenu = () => {
    setAnchorEl(null);
    setCurrentMaterialId(null);
    setGeneratedSummaries([]);
    setGeneratedFlashcards([]);
    setGeneratedQuizzes([]);
    setLoadingGenerated(false);
    setErrorGenerated('');
  };

  const handleExport = async (materialType: string, materialId: number, format: string) => {
    try {
      await exportGeneratedMaterial(materialType, materialId, format);
      handleCloseExportMenu();
    } catch (err: any) {
      setErrorGenerated(err.message || 'Export failed.');
    }
  };


  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          width: '100%',
          maxWidth: '1200px', // Increased width for better table display
          padding: 3,
          boxShadow: 3,
          borderRadius: 2,
          bgcolor: 'background.paper',
          textAlign: 'center',
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to your Dashboard!
        </Typography>

        {/* Next Step Suggestion Section */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" component="h2" gutterBottom>
            Next Step Suggestion
          </Typography>
          <TextField
            label="Your Query"
            fullWidth
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loadingSuggestion}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleGetSuggestion}
            disabled={loadingSuggestion || !query.trim()}
            sx={{ mt: 2 }}
          >
            {loadingSuggestion ? <CircularProgress size={24} /> : 'Get Suggestion'}
          </Button>

          {errorSuggestion && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {errorSuggestion}
            </Alert>
          )}

          {nextStep && (
            <Box sx={{ mt: 2, p: 2, border: '1px solid #ccc', borderRadius: 1, textAlign: 'left' }}>
              <Typography variant="h6">Suggested Next Step:</Typography>
              <Typography>AI Module: {nextStep.ai_module}</Typography>
              <Typography>Interaction Pattern: {nextStep.interaction_pattern}</Typography>
              {/* Render other NextStep details as needed */}
            </Box>
          )}
        </Box>

        {/* Study Materials Overview Section */}
        <Box sx={{ mt: 4, width: '100%' }}>
          <Typography variant="h6" component="h2" gutterBottom>
            Your Study Materials
          </Typography>
          {loadingMaterials ? (
            <CircularProgress />
          ) : errorMaterials ? (
            <Alert severity="error">{errorMaterials}</Alert>
          ) : studyMaterials.length === 0 ? (
            <Typography>You haven't uploaded any study materials yet.</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="study materials table">
                <TableHead>
                  <TableRow>
                    <TableCell>File Name</TableCell>
                    <TableCell align="right">Upload Date</TableCell>
                    <TableCell align="right">Processing Status</TableCell>
                    <TableCell align="center">Actions</TableCell> {/* New column */}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {studyMaterials.map((material) => (
                    <TableRow
                      key={material.id}
                      sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                      <TableCell component="th" scope="row">
                        {material.file_name}
                      </TableCell>
                      <TableCell align="right">
                        {new Date(material.upload_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">{material.processing_status}</TableCell>
                      <TableCell align="center">
                        <IconButton
                          aria-label="more"
                          aria-controls={`long-menu-${material.id}`}
                          aria-haspopup="true"
                          onClick={(event) => handleOpenExportMenu(event, material.id)}
                          disabled={loadingGenerated && currentMaterialId === material.id}
                        >
                          {loadingGenerated && currentMaterialId === material.id ? <CircularProgress size={20} /> : <MoreVertIcon />}
                        </IconButton>
                        <Menu
                          id={`long-menu-${material.id}`}
                          MenuListProps={{
                            'aria-labelledby': 'long-button',
                          }}
                          anchorEl={anchorEl}
                          open={Boolean(anchorEl) && currentMaterialId === material.id}
                          onClose={handleCloseExportMenu}
                          PaperProps={{
                            style: {
                              maxHeight: 48 * 4.5,
                              width: '20ch',
                            },
                          }}
                        >
                          {errorGenerated && currentMaterialId === material.id && (
                            <MenuItem disabled sx={{ color: 'error.main' }}>
                              {errorGenerated}
                            </MenuItem>
                          )}
                          {!loadingGenerated && currentMaterialId === material.id && (
                            <>
                              {generatedSummaries.length > 0 && generatedSummaries.map((summary) => (
                                <Box key={`summary-${summary.id}`}>
                                  <MenuItem onClick={() => handleExport('summary', summary.id, 'pdf')}>
                                    Summary ({summary.id}) - PDF
                                  </MenuItem>
                                  <MenuItem onClick={() => handleExport('summary', summary.id, 'docx')}>
                                    Summary ({summary.id}) - DOCX
                                  </MenuItem>
                                </Box>
                              ))}
                              {generatedFlashcards.length > 0 && generatedFlashcards.map((flashcardSet) => (
                                <Box key={`flashcard-${flashcardSet.id}`}>
                                  <MenuItem onClick={() => handleExport('flashcard_set', flashcardSet.id, 'pdf')}>
                                    Flashcards ({flashcardSet.id}) - PDF
                                  </MenuItem>
                                  <MenuItem onClick={() => handleExport('flashcard_set', flashcardSet.id, 'docx')}>
                                    Flashcards ({flashcardSet.id}) - DOCX
                                  </MenuItem>
                                  <MenuItem onClick={() => handleExport('flashcard_set', flashcardSet.id, 'csv')}>
                                    Flashcards ({flashcardSet.id}) - CSV
                                  </MenuItem>
                                </Box>
                              ))}
                              {generatedQuizzes.length > 0 && generatedQuizzes.map((quiz) => (
                                <Box key={`quiz-${quiz.id}`}>
                                  <MenuItem onClick={() => handleExport('quiz', quiz.id, 'pdf')}>
                                    Quiz ({quiz.id}) - PDF
                                  </MenuItem>
                                  <MenuItem onClick={() => handleExport('quiz', quiz.id, 'docx')}>
                                    Quiz ({quiz.id}) - DOCX
                                  </MenuItem>
                                  <MenuItem onClick={() => handleExport('quiz', quiz.id, 'csv')}>
                                    Quiz ({quiz.id}) - CSV
                                  </MenuItem>
                                </Box>
                              ))}
                              {generatedSummaries.length === 0 && generatedFlashcards.length === 0 && generatedQuizzes.length === 0 && (
                                <MenuItem disabled>No generated materials</MenuItem>
                              )}
                            </>
                          )}
                        </Menu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>

        <Button variant="contained" color="primary" onClick={() => router.push('/')} sx={{ mt: 4 }}>
          Go to Home
        </Button>
        <Button variant="outlined" color="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </Box>
    </main>
  );
}
