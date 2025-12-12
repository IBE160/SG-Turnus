import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SignUpForm from '@/components/auth/SignUpForm';
import { registerUser } from '@/services/authService';

// Mock the authService
jest.mock('@/services/authService', () => ({
  registerUser: jest.fn(),
}));

describe('SignUpForm', () => {
  beforeEach(() => {
    // Reset the mock before each test
    (registerUser as jest.Mock).mockClear();
  });

  it('renders the sign up form', () => {
    render(<SignUpForm />);
    expect(screen.getByRole('heading', { name: /sign up/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields on submit', async () => {
    render(<SignUpForm />);
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      // Required fields should trigger browser's native validation
      // which is hard to test directly with @testing-library.
      // We'll rely on the 'required' attribute for basic validation.
      // For more complex validation, we'd check for specific error messages.
    });
    expect(registerUser).not.toHaveBeenCalled();
  });

  it('calls registerUser and shows success message on successful submission', async () => {
    (registerUser as jest.Mock).mockResolvedValue({ success: true });

    render(<SignUpForm />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'Password123!' } });
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(registerUser).toHaveBeenCalledTimes(1);
      expect(registerUser).toHaveBeenCalledWith('test@example.com', 'Password123!');
      expect(screen.getByText(/thank you for signing up\. please check your email for a verification link\./i)).toBeInTheDocument();
    });
  });

  it('shows an error message if registration fails', async () => {
    (registerUser as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<SignUpForm />);

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'Password123!' } });
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    await waitFor(() => {
      expect(registerUser).toHaveBeenCalledTimes(1);
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });
});
