"use client";

import { useEffect, useState } from 'react'; // Import useState
import { useSocket } from '../contexts/SocketContext';
import WebSocketTester from '../components/WebSocketTester';
import ShareDialog from '../components/ShareDialog'; // Import the ShareDialog component
import { Button, Box } from '@mui/material'; // Import MUI components

export const metadata = {
  title: 'The AI Helping Tool - Your Smart Companion for Learning and Productivity',
  description: 'Empower your learning with AI-powered study assistance. Get instant clarity, generate study materials, and boost your productivity.',
};

export default function Home() {
  const { isConnected } = useSocket();
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);

  useEffect(() => {
    console.log("Home component: WebSocket Connected Status:", isConnected);
  }, [isConnected]);

  const handleOpenShareDialog = () => {
    setIsShareDialogOpen(true);
  };

  const handleCloseShareDialog = () => {
    setIsShareDialogOpen(false);
  };

  return (
    <div>
      <h1>Welcome to The AI Helping Tool</h1>
      <h2>Your Smart Companion for Learning and Productivity</h2>
      <p>The project is successfully initialized and running. Start your journey towards enhanced learning and productivity with AI-powered assistance.</p>
      
      <Box mt={4}>
        <Button variant="contained" color="primary" onClick={handleOpenShareDialog}>
          Share Dummy Study Material
        </Button>
      </Box>

      <WebSocketTester />

      <ShareDialog
        open={isShareDialogOpen}
        onClose={handleCloseShareDialog}
        studyMaterialId={1} // Dummy ID for demonstration
        studyMaterialFileName="My Awesome Study Notes.pdf" // Dummy name
      />
    </div>
  );
}
