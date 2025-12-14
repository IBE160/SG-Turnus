'use client';

import { useState } from 'react';
import { TextField, Button, Box, Typography } from '@mui/material';
import { loginUser } from '@/services/authService'; // Will create this function
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await loginUser(email, password);
      // Assuming a successful login returns a token and we need to store it
      // For now, just logging and redirecting. Actual token storage (e.g., cookies)
      // will be handled by a more complete auth flow or the authService itself.
      console.log('Login successful:', response);
      router.push('/dashboard'); // Redirect to dashboard or a protected route
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred during login.');
      console.error('Login error:', err);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        width: '100%',
      }}
    >
      {error && <Typography color="error">{error}</Typography>}
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        fullWidth
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        fullWidth
      />
      <Button type="submit" variant="contained" fullWidth>
        Login
      </Button>
      {/* Optional: Add links for sign-up, forgot password, etc. */}
      <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
        Don't have an account? <a href="/signup">Sign Up</a>
      </Typography>
    </Box>
  );
}
