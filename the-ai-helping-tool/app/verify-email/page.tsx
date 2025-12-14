'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const email = searchParams.get('email');
  const token = searchParams.get('token');

  const [message, setMessage] = useState(
    (!email || !token) ? 'Verification Failed' : 'Verifying your email...'
  );
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(
    (!email || !token) ? 'Verification link is incomplete. Please ensure you have the correct email and token.' : null
  );

  useEffect(() => {
    // If email or token are missing, initial state already reflects the error,
    // so no need to proceed with verification.
    if (!email || !token) {
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, token }),
        });

        const data = await response.json();

        if (response.ok) {
          setMessage(data.message || 'Email verified successfully!');
          setIsSuccess(true);
        } else {
          setError(data.detail || 'An unexpected error occurred during verification.');
          setMessage('Verification Failed');
        }
      } catch (err) {
        console.error('Email verification error:', err);
        setError('Failed to connect to the server. Please try again later.');
        setMessage('Verification Failed');
      }
    };

    verifyEmail();
  }, [searchParams, router, email, token]);

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>{message}</h1>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {isSuccess && (
        <p>
          Your email has been successfully verified. You can now{' '}
          <Link href="/login">
            <span style={{ color: 'blue', cursor: 'pointer', textDecoration: 'underline' }}>log in</span>
          </Link>
          .
        </p>
      )}
      {!isSuccess && !error && (
        <p>
          If you were redirected here by mistake or the link is invalid, please check your email or{' '}
          <Link href="/register">
            <span style={{ color: 'blue', cursor: 'pointer', textDecoration: 'underline' }}>register again</span>
          </Link>
          .
        </p>
      )}
    </div>
  );
}
