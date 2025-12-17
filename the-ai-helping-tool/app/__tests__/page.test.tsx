import { render, screen } from '@testing-library/react';
import Home, { metadata } from '../page';

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
    render(<Home />);
    const heading = screen.getByRole('heading', { level: 1, name: 'Welcome to The AI Helping Tool' });
    expect(heading).toBeInTheDocument();
  });

  it('should render the subheading (h2)', () => {
    render(<Home />);
    const subheading = screen.getByRole('heading', { level: 2, name: 'Your Smart Companion for Learning and Productivity' });
    expect(subheading).toBeInTheDocument();
  });
});

