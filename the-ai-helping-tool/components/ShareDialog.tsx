import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Box,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { StudyMaterialResponse } from '../../services/studyMaterialService';
import { shareWithUser, generateShareLink } from '../../services/sharingService'; // Assuming a new sharing service
import { useAuth } from '../../contexts/AuthContext';

interface ShareDialogProps {
  open: boolean;
  onClose: () => void;
  material: StudyMaterialResponse | null;
}

const ShareDialog: React.FC<ShareDialogProps> = ({ open, onClose, material }) => {
  const { token } = useAuth();
  const [shareOption, setShareOption] = useState<'link' | 'user'>('link');
  const [permissions, setPermissions] = useState<'view' | 'edit'>('view');
  const [email, setEmail] = useState('');
  const [generatedLink, setGeneratedLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleShare = async () => {
    if (!material || !token) return;

    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    setGeneratedLink(null);

    try {
      if (shareOption === 'link') {
        const link = await generateShareLink(token, material.id, permissions);
        setGeneratedLink(link);
        setSuccessMessage('Successfully generated shareable link!');
      } else {
        await shareWithUser(token, material.id, email, permissions);
        setSuccessMessage(`Successfully shared with ${email}!`);
      }
    } catch (err) {
      setError('Failed to share. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
    // Reset state on close
    setTimeout(() => {
        setShareOption('link');
        setPermissions('view');
        setEmail('');
        setGeneratedLink(null);
        setError(null);
        setSuccessMessage(null);
    }, 300);
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>Share {material?.file_name || 'Study Material'}</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {successMessage && <Alert severity="success" sx={{ mb: 2 }}>{successMessage}</Alert>}
        
        <FormControl component="fieldset" margin="normal">
          <FormLabel component="legend">Share Option</FormLabel>
          <RadioGroup row value={shareOption} onChange={(e) => setShareOption(e.target.value as 'link' | 'user')}>
            <FormControlLabel value="link" control={<Radio />} label="Generate Link" />
            <FormControlLabel value="user" control={<Radio />} label="Share with User" />
          </RadioGroup>
        </FormControl>

        {shareOption === 'user' && (
          <TextField
            autoFocus
            margin="dense"
            label="Classmate's Email"
            type="email"
            fullWidth
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        )}

        <FormControl component="fieldset" margin="normal">
          <FormLabel component="legend">Permissions</FormLabel>
          <RadioGroup row value={permissions} onChange={(e) => setPermissions(e.target.value as 'view' | 'edit')}>
            <FormControlLabel value="view" control={<Radio />} label="View-Only" />
            <FormControlLabel value="edit" control={<Radio />} label="Collaborate (Edit)" />
          </RadioGroup>
        </FormControl>

        {generatedLink && (
          <Box sx={{ mt: 2, p: 1, border: '1px solid #ccc', borderRadius: 1 }}>
            <Typography variant="body2">Share this link:</Typography>
            <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>{`${window.location.origin}/share/${generatedLink}`}</Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleShare} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Share'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ShareDialog;