"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Container, Typography, Box, CircularProgress, Alert } from '@mui/material';
import sharingService, { SharedMaterialResponse } from '../../../services/sharingService';

interface SharePageProps {
  params: { token: string };
}

const SharePage: React.FC<SharePageProps> = ({ params }) => {
  const { token } = params;
  const [sharedMaterial, setSharedMaterial] = useState<SharedMaterialResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      const fetchSharedMaterial = async () => {
        try {
          setLoading(true);
          const material = await sharingService.getSharedMaterialByToken(token);
          setSharedMaterial(material);
        } catch (err) {
          setError('Failed to load shared material or link is invalid/expired.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchSharedMaterial();
    }
  }, [token]);

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

  if (!sharedMaterial) {
    return (
      <Container>
        <Alert severity="warning">No shared material found.</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Shared Study Material: {sharedMaterial.file_name}
        </Typography>
        <Typography variant="body1" paragraph>
          This material has been shared with you with '{sharedMaterial.permissions}' permissions.
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Uploaded by User ID: {sharedMaterial.shared_by_user_id}
        </Typography>
        {sharedMaterial.expires_at && (
            <Typography variant="body2" color="textSecondary">
                Expires on: {new Date(sharedMaterial.expires_at).toLocaleString()}
            </Typography>
        )}
        {/* Here you would typically display the actual content of the study material.
            For now, we're just displaying its metadata. */}
        <Box sx={{ mt: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: '8px' }}>
            <Typography variant="h6">Material Details (Placeholder)</Typography>
            <Typography>File Name: {sharedMaterial.file_name}</Typography>
            <Typography>S3 Key: {sharedMaterial.s3_key}</Typography>
            {/* Implement logic to fetch and display actual content based on s3_key and permissions */}
            <Typography sx={{ mt: 2, fontStyle: 'italic', color: 'gray' }}>
                (Content display for "{sharedMaterial.file_name}" to be implemented based on S3 integration and material type.)
            </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default SharePage;
