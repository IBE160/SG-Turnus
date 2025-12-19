import { render, screen } from '@testing-library/react';
import { SocketProvider } from '../../contexts/SocketContext';
import Home, { metadata } from '../page';

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    refresh: jest.fn(),
  }),
}));

describe('Home Page Metadata', () => {
  it('should have the correct title', () => {
    expect(metadata.title).toBe('The AI Helping Tool - Your Smart Companion for Learning and Productivity');
  });

  it('should have the correct meta description', () => {
    expect(metadata.description).toBe('Empower your learning with AI-powered study assistance. Get instant clarity, generate study materials, and boost your productivity.');
  });
});

describe('Home Page Content', () => {
  it('should render the main heading (h1)', () => {
    render(
      <SocketProvider>
        <Home />
      </SocketProvider>
    );
    const heading = screen.getByRole('heading', { level: 1, name: 'Welcome to The AI Helping Tool' });
    expect(heading).toBeInTheDocument();
  });

  it('should render the subheading (h2)', () => {
    render(
      <SocketProvider>
        <Home />
      </SocketProvider>
    );
    const subheading = screen.getByRole('heading', { level: 2, name: 'Your Smart Companion for Learning and Productivity' });
    expect(subheading).toBeInTheDocument();
  });
});
