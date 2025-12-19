"use client";

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  getStudyMaterials,
  StudyMaterialResponse,
  GeneratedSummaryResponse,
  GeneratedFlashcardSetResponse,
  GeneratedQuizResponse,
} from '../../services/studyMaterialService';
import { useSocket } from '../../contexts/SocketContext';
import { useAuth } from '../../contexts/AuthContext';
import { useSync } from '../../contexts/SyncContext';
import Link from 'next/link';

const DashboardPage: React.FC = () => {
  const { socket } = useSocket();
  const { token } = useAuth();
  const { updatedMaterials } = useSync();
  const [studyMaterials, setStudyMaterials] = useState<StudyMaterialResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      const fetchStudyMaterials = async () => {
        try {
          setLoading(true);
          const materials = await getStudyMaterials(token);
          setStudyMaterials(materials);
        } catch (err) {
          setError('Failed to fetch study materials.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchStudyMaterials();

      if (socket) {
        socket.on('study_material_created', (data: StudyMaterialResponse) => {
          setStudyMaterials((prev) => [...prev, data]);
        });
        socket.on('study_material_updated', (data: StudyMaterialResponse) => {
          setStudyMaterials((prev) => prev.map((sm) => (sm.id === data.id ? data : sm)));
        });
        socket.on('study_material_deleted', (data: { id: number }) => {
          setStudyMaterials((prev) => prev.filter((sm) => sm.id !== data.id));
        });
        socket.on('summary_created', (data: GeneratedSummaryResponse) => {
          setStudyMaterials((prev) =>
            prev.map((sm) =>
              sm.id === data.study_material_id
                ? { ...sm, generated_summaries: [...(sm.generated_summaries || []), data] }
                : sm
            )
          );
        });
        socket.on('flashcards_created', (data: GeneratedFlashcardSetResponse) => {
          setStudyMaterials((prev) =>
            prev.map((sm) =>
              sm.id === data.study_material_id
                ? { ...sm, generated_flashcard_sets: [...(sm.generated_flashcard_sets || []), data] }
                : sm
            )
          );
        });
        socket.on('quiz_created', (data: GeneratedQuizResponse) => {
          setStudyMaterials((prev) =>
            prev.map((sm) =>
              sm.id === data.study_material_id
                ? { ...sm, generated_quizzes: [...(sm.generated_quizzes || []), data] }
                : sm
            )
          );
        });

        return () => {
          socket.off('study_material_created');
          socket.off('study_material_updated');
          socket.off('study_material_deleted');
          socket.off('summary_created');
          socket.off('flashcards_created');
          socket.off('quiz_created');
        };
      }
    }
  }, [token, socket]);

  useEffect(() => {
    if (updatedMaterials.length > 0) {
      setStudyMaterials((prev) => {
        const updated = [...prev];
        updatedMaterials.forEach((material) => {
          const index = updated.findIndex((m) => m.id === material.id);
          if (index !== -1) {
            updated[index] = material;
          } else {
            updated.push(material);
          }
        });
        return updated;
      });
    }
  }, [updatedMaterials]);


  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Alert severity="info" sx={{ mb: 2 }}>
        This is an MVP demo. Some functionality is mocked.
      </Alert>
      <Typography variant="h4" component="h1" gutterBottom>
        My Study Materials Dashboard
      </Typography>

      {studyMaterials.length === 0 ? (
        <Typography>You have not uploaded any study materials yet.</Typography>
      ) : (
        <List>
          {studyMaterials.map((material) => (
            <Box key={material.id} sx={{ mb: 2 }}>
              <Accordion>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls={`panel-${material.id}-content`}
                  id={`panel-${material.id}-header`}
                >
                  <Typography variant="h6">{material.file_name}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="textSecondary">
                    Upload Date: {new Date(material.upload_date).toLocaleDateString()} | Status: {material.processing_status}
                  </Typography>
                  <Button variant="outlined" size="small" sx={{ mt: 1, mr: 1 }}>
                    View Material
                  </Button>
                  {/* Link to generate new content from this material */}
                  <Link href={`/generate/${material.id}`} passHref>
                    <Button variant="outlined" size="small" sx={{ mt: 1 }}>
                      Generate New Content
                    </Button>
                  </Link>

                  {material.generated_summaries && material.generated_summaries.length > 0 && (
                    <Box mt={2}>
                      <Typography variant="subtitle1">Summaries:</Typography>
                      <List disablePadding>
                        {material.generated_summaries.map((summary) => (
                          <ListItem key={summary.id} dense>
                            <ListItemText
                              primary={`Summary (Detail: ${summary.detail_level})`}
                              secondary={summary.content.substring(0, 100) + '...'} // Show snippet
                            />
                            <Button size="small">View</Button>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {material.generated_flashcard_sets && material.generated_flashcard_sets.length > 0 && (
                    <Box mt={2}>
                      <Typography variant="subtitle1">Flashcard Sets:</Typography>
                      <List disablePadding>
                        {material.generated_flashcard_sets.map((flashcardSet) => (
                          <ListItem key={flashcardSet.id} dense>
                            <ListItemText
                              primary={`Flashcard Set (${flashcardSet.content.length} cards)`}
                              secondary={`Generated: ${new Date(flashcardSet.generated_at).toLocaleDateString()}`}
                            />
                            <Button size="small">View</Button>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {material.generated_quizzes && material.generated_quizzes.length > 0 && (
                    <Box mt={2}>
                      <Typography variant="subtitle1">Quizzes:</Typography>
                      <List disablePadding>
                        {material.generated_quizzes.map((quiz) => (
                          <ListItem key={quiz.id} dense>
                            <ListItemText
                              primary={`Quiz (${quiz.content.length} questions)`}
                              secondary={`Generated: ${new Date(quiz.generated_at).toLocaleDateString()}`}
                            />
                            <Button size="small">View</Button>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>
            </Box>
          ))}
        </List>
      )}
    </Container>
  );
};

export default DashboardPage;