"use client";

import { useState } from 'react';
import { generateFlashcards, Flashcard } from '../../../services/studyMaterialService'; // Adjust path as needed

export default function FlashcardsPage() {
  const [textToProcess, setTextToProcess] = useState('');
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateFlashcards = async () => {
    setLoading(true);
    setError('');
    setFlashcards([]);
    try {
      const response = await generateFlashcards({ text: textToProcess });
      setFlashcards(response.flashcards);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>Flashcard Generator</h1>
      <p>Enter text below to generate flashcards (question/answer pairs).</p>

      <textarea
        value={textToProcess}
        onChange={(e) => setTextToProcess(e.target.value)}
        placeholder="Paste your study material here..."
        rows={15}
        style={{ width: '100%', padding: '10px', marginBottom: '20px', border: '1px solid #ccc', borderRadius: '4px' }}
      />

      <button
        onClick={handleGenerateFlashcards}
        disabled={loading || !textToProcess.trim()}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? 'Generating Flashcards...' : 'Generate Flashcards'}
      </button>

      {error && (
        <p style={{ color: 'red', marginTop: '20px' }}>Error: {error}</p>
      )}

      {flashcards.length > 0 && (
        <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h2>Generated Flashcards</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
            {flashcards.map((fc, index) => (
              <div key={index} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#fdfdfd' }}>
                <p><strong>Q:</strong> {fc.question}</p>
                <p><strong>A:</strong> {fc.answer}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
