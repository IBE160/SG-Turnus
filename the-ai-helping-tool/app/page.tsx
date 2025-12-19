"use client";

import { useEffect } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { Button, Box, Typography, Container } from '@mui/material'; // Import MUI components
import Link from 'next/link';

export default function Home() {
  const { isConnected } = useSocket();

  useEffect(() => {
    console.log("Home component: WebSocket Connected Status:", isConnected);
  }, [isConnected]);

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to The AI Helping Tool
        </Typography>
        <Typography variant="h5" component="h2" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Your Smart Companion for Learning and Productivity
        </Typography>
        <Typography variant="body1" align="center" sx={{ mb: 2 }}>
          This is an MVP demo for a student exam project. Some functionality is mocked or simplified.
        </Typography>
        <Typography variant="body1" align="center" sx={{ mb: 4 }}>
          Get started by viewing your study materials on the dashboard.
        </Typography>
        <Link href="/dashboard" passHref>
          <Button variant="contained" color="primary" size="large">
            Go to Dashboard
          </Button>
        </Link>
      </Box>
    </Container>
  );
}
