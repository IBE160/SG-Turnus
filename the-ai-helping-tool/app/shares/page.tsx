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
  Tabs,
  Tab,
  Button,
} from '@mui/material';
import sharingService, { SharedMaterialResponse } from '../../services/sharingService';
import { useSocket } from '../../contexts/SocketContext'; // Assuming this provides the token

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const SharesPage: React.FC = () => {
  const { socket } = useSocket(); // Assuming useSocket provides the token
  const [myShares, setMyShares] = useState<SharedMaterialResponse[]>([]);
  const [sharedWithMe, setSharedWithMe] = useState<SharedMaterialResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [value, setValue] = useState(0); // State for tab selection
  const [token, setToken] = useState<string | null>(null); // State to hold the auth token


  useEffect(() => {
    // In a real application, fetch the actual token from your authentication context or local storage.
    // For this demonstration, we'll use the dummy token from layout.tsx.
    const dummyToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.Pz13-hE2o27zWlD201b1Q3o43-F4f4f4f4f4f4f4f4f";
    setToken(dummyToken);
  }, []);


  useEffect(() => {
    if (token) {
      const fetchShares = async () => {
        try {
          setLoading(true);
          const [my, withMe] = await Promise.all([
            sharingService.getMyShares(token),
            sharingService.getSharedWithMe(token),
          ]);
          setMyShares(my);
          setSharedWithMe(withMe);
        } catch (err) {
          setError('Failed to fetch shares.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchShares();
    }
  }, [token]);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const handleRevokeShare = async (shareId: number) => {
    if (!token) return;
    try {
      await sharingService.revokeShare(shareId, token);
      // Refresh shares after revoking
      const [my, withMe] = await Promise.all([
        sharingService.getMyShares(token),
        sharingService.getSharedWithMe(token),
      ]);
      setMyShares(my);
      setSharedWithMe(withMe);
    } catch (err) {
      setError('Failed to revoke share.');
      console.error(err);
    }
  };


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
      <Typography variant="h4" component="h1" gutterBottom>
        Shared Materials
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="shared materials tabs">
          <Tab label="My Shares" {...a11yProps(0)} />
          <Tab label="Shared With Me" {...a11yProps(1)} />
        </Tabs>
      </Box>

      <CustomTabPanel value={value} index={0}>
        <Typography variant="h5" gutterBottom>
          Materials I have shared:
        </Typography>
        {myShares.length === 0 ? (
          <Typography>You haven't shared any materials yet.</Typography>
        ) : (
          <List>
            {myShares.map((share) => (
              <ListItem key={share.id} divider>
                <ListItemText
                  primary={share.file_name}
                  secondary={
                    <Box component="span">
                      Shared with: {share.shared_with_user_id ? `User ID ${share.shared_with_user_id}` : `Public link`} (Permissions: {share.permissions})
                      {share.share_token && (
                        <Typography component="span" variant="body2" display="block">
                          Link: {window.location.origin}/share/{share.share_token}
                        </Typography>
                      )}
                      {share.expires_at && (
                        <Typography component="span" variant="body2" display="block">
                          Expires: {format(new Date(share.expires_at), 'PPPp')}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Button variant="outlined" color="secondary" onClick={() => handleRevokeShare(share.id)}>
                  Revoke
                </Button>
              </ListItem>
            ))}
          </List>
        )}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={1}>
        <Typography variant="h5" gutterBottom>
          Materials shared with me:
        </Typography>
        {sharedWithMe.length === 0 ? (
          <Typography>No materials have been shared with you yet.</Typography>
        ) : (
          <List>
            {sharedWithMe.map((share) => (
              <ListItem key={share.id} divider>
                <ListItemText
                  primary={share.file_name}
                  secondary={
                    <Box component="span">
                      Shared by: User ID {share.shared_by_user_id} (Permissions: {share.permissions})
                      {share.expires_at && (
                        <Typography component="span" variant="body2" display="block">
                          Expires: {format(new Date(share.expires_at), 'PPPp')}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </CustomTabPanel>
    </Container>
  );
};

export default SharesPage;