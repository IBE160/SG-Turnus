import { metadata } from '../layout'; // Assuming layout.tsx exports metadata

describe('Metadata in layout.tsx', () => {
  it('should have the correct title', () => {
    expect(metadata.title).toBe('The AI Helping Tool');
  });

  it('should have the correct description', () => {
    expect(metadata.description).toBe('An AI-powered tool to help you learn and study more effectively.');
  });
});
