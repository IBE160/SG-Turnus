'use client';

import { useState } from 'react';
import { TextField, Button, Box, Typography } from '@mui/material';
import { loginUser } from '@/services/authService';
import { useRouter } from 'next/navigation';

// Email validation regex (simple but effective for client-side)
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Password validation function (copied from SignUpForm for consistency)
const validatePassword = (password: string): string | null => {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long.';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter.';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter.';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number.';
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).';
  }
  return null; // Password is valid
};

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [submissionError, setSubmissionError] = useState<string | null>(null); // Renamed to avoid confusion with validation errors
  const router = useRouter();

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    if (newEmail && !EMAIL_REGEX.test(newEmail)) {
      setEmailError('Please enter a valid email address.');
    } else {
      setEmailError(null);
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordError(validatePassword(newPassword));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmissionError(null); // Clear previous submission errors

    // Re-run validation before submission
    const currentEmailError = email ? (EMAIL_REGEX.test(email) ? null : 'Please enter a valid email address.') : 'Email is required.';
    const currentPasswordError = validatePassword(password);

    setEmailError(currentEmailError);
    setPasswordError(currentPasswordError);

    if (currentEmailError || currentPasswordError || !email || !password) {
      return; // Prevent submission if there are validation errors or empty fields
    }

    try {
      const response = await loginUser(email, password);
      console.log('Login successful:', response);
      router.push('/dashboard');
    } catch (err) {
      setSubmissionError(err instanceof Error ? err.message : 'An unknown error occurred during login.');
      console.error('Login error:', err);
    }
  };

  const isFormValid = !emailError && !passwordError && email && password;

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
      {submissionError && <Typography color="error">{submissionError}</Typography>}
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={handleEmailChange}
        onBlur={handleEmailChange} // Validate on blur as well
        required
        fullWidth
        error={!!emailError}
        helperText={emailError}
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={handlePasswordChange}
        onBlur={handlePasswordChange} // Validate on blur as well
        required
        fullWidth
        error={!!passwordError}
        helperText={passwordError || "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."}
      />
      <Button type="submit" variant="contained" fullWidth disabled={!isFormValid}>
        Login
      </Button>
      <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
        Don&apos;t have an account? <a href="/signup">Sign Up</a>
      </Typography>
    </Box>
  );
}

