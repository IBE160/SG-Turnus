// the-ai-helping-tool/app/dashboard/page.tsx
'use client';

import { Typography, Box, Button } from '@mui/material';
import { useRouter } from 'next/navigation';
import { logoutUser } from '@/services/authService';

export default function DashboardPage() {
  const router = useRouter();

  const handleLogout = () => {
    logoutUser();
    router.push('/login'); // Redirect to login page after logout
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          width: '100%',
          maxWidth: '600px',
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
        <Typography variant="body1">
          This is a placeholder for your personalized study materials.
        </Typography>
        <Button variant="contained" color="primary" onClick={() => router.push('/')}>
          Go to Home
        </Button>
        <Button variant="outlined" color="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </Box>
    </main>
  );
}
