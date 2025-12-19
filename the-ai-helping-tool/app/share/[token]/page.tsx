"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Button,
} from '@mui/material';
import { getSharedMaterial } from '../../../services/sharingService';
import { useAuth } from '../../../contexts/AuthContext';

const SharedMaterialPage: React.FC = () => {
  const { token } = useAuth();
  const params = useParams();
  const shareToken = params.token as string;

  const [material, setMaterial] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (shareToken) {
      const fetchMaterial = async () => {
        try {
          setLoading(true);
          const sharedMaterial = await getSharedMaterial(shareToken, token || undefined);
          setMaterial(sharedMaterial);
        } catch (err) {
          setError('Failed to retrieve shared material. The link may be invalid, expired, or you might not have permission to view it.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchMaterial();
    }
  }, [shareToken, token]);

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

  if (!material) {
    return (
      <Container>
        <Alert severity="info">No material to display.</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {material.file_name}
        </Typography>
        <Typography variant="body1" gutterBottom>
          This material has been shared with you.
        </Typography>
        <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
          Permissions: {material.permissions}
        </Typography>
        
        {/* Here you would render the actual content of the study material */}
        {/* This is a placeholder for where the material's content would be displayed */}
        <Box sx={{ my: 3, p: 2, border: '1px dashed grey', minHeight: 200 }}>
          <Typography variant="body2" color="textSecondary">
            (Content of the study material would be rendered here based on its type and S3 key: {material.s3_key})
          </Typography>
        </Box>

        <Button variant="contained">Download Material</Button>
      </Paper>
    </Container>
  );
};

export default SharedMaterialPage;