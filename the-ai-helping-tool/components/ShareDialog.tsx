"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Snackbar,
  Alert,
  Box,
} from '@mui/material';
import sharingService, { Permissions, ShareCreateRequest, SharedLinkResponse } from '../services/sharingService';
import { useSocket } from '../contexts/SocketContext'; // Assuming you have a way to get the token
import { format } from 'date-fns'; // For formatting date/time

interface ShareDialogProps {
  open: boolean;
  onClose: () => void;
  studyMaterialId: number;
  studyMaterialFileName: string;
}

const ShareDialog: React.FC<ShareDialogProps> = ({ open, onClose, studyMaterialId, studyMaterialFileName }) => {
  const router = useRouter();
  const { socket } = useSocket(); // Assuming useSocket provides the token, or you get it from another auth context
  const [sharedWithEmail, setSharedWithEmail] = useState<string>('');
  const [permissions, setPermissions] = useState<Permissions>(Permissions.VIEW_ONLY);
  const [expiresAt, setExpiresAt] = useState<string>(''); // ISO 8601 string for date-time input
  const [shareLink, setShareLink] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');
  const [token, setToken] = useState<string | null>(null); // State to hold the auth token

  useEffect(() => {
    // In a real application, fetch the actual token from your authentication context or local storage.
    // For this demonstration, we'll use the dummy token from layout.tsx.
    const dummyToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.Pz13-hE2o27zWlD201b1Q3o43-F4f4f4f4f4f4f4f4f";
    setToken(dummyToken);
  }, []);

  const handleShare = async () => {
    if (!token) {
      setSnackbarMessage('Authentication token not available. Cannot share.');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }

    try {
      const shareData: ShareCreateRequest = {
        study_material_id: studyMaterialId,
        permissions,
        expires_at: expiresAt || undefined, // Only send if not empty
      };

      if (sharedWithEmail) {
        shareData.shared_with_email = sharedWithEmail;
      }

      const response = await sharingService.createShare(shareData, token);

      if (response.share_token) {
        const fullLink = `${window.location.origin}/share/${response.share_token}`;
        setShareLink(fullLink);
        setSnackbarMessage('Share link generated successfully!');
      } else if (response.shared_with_user_id) {
        setSnackbarMessage(`Material shared with ${sharedWithEmail} successfully!`);
      }
      setSnackbarSeverity('success');
    } catch (error) {
      console.error('Failed to create share:', error);
      setSnackbarMessage('Failed to create share.');
      setSnackbarSeverity('error');
    } finally {
      setSnackbarOpen(true);
    }
  };

  const handleCopyLink = () => {
    if (shareLink) {
      navigator.clipboard.writeText(shareLink);
      setSnackbarMessage('Share link copied to clipboard!');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  const resetDialog = () => {
    setSharedWithEmail('');
    setPermissions(Permissions.VIEW_ONLY);
    setExpiresAt('');
    setShareLink(null);
    setSnackbarOpen(false);
    setSnackbarMessage('');
    setSnackbarSeverity('success');
    onClose();
  };

  return (
    <>
      <Dialog open={open} onClose={resetDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Share Study Material: {studyMaterialFileName}</DialogTitle>
        <DialogContent dividers>
          <Box mb={2}>
            <TextField
              autoFocus
              margin="dense"
              id="shared-with-email"
              label="Share with Email (optional)"
              type="email"
              fullWidth
              variant="outlined"
              value={sharedWithEmail}
              onChange={(e) => setSharedWithEmail(e.target.value)}
              helperText="Leave empty to generate a public shareable link"
            />
          </Box>
          <Box mb={2}>
            <FormControl fullWidth margin="dense" variant="outlined">
              <InputLabel id="permissions-label">Permissions</InputLabel>
              <Select
                labelId="permissions-label"
                id="permissions"
                value={permissions}
                label="Permissions"
                onChange={(e) => setPermissions(e.target.value as Permissions)}
              >
                <MenuItem value={Permissions.VIEW_ONLY}>View Only</MenuItem>
                <MenuItem value={Permissions.EDIT}>Edit (Not yet implemented)</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box mb={2}>
            <TextField
              id="expires-at"
              label="Expiration Date (optional)"
              type="datetime-local"
              fullWidth
              variant="outlined"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              InputLabelProps={{
                shrink: true,
              }}
              helperText="Leave empty for no expiration"
            />
          </Box>

          {shareLink && (
            <Box mt={3}>
              <Typography variant="h6">Shareable Link:</Typography>
              <TextField
                fullWidth
                variant="outlined"
                value={shareLink}
                InputProps={{
                  readOnly: true,
                }}
                sx={{ mt: 1 }}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleCopyLink}
                sx={{ mt: 1 }}
              >
                Copy Link
              </Button>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={resetDialog} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleShare} color="primary" variant="contained">
            Share
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default ShareDialog;
