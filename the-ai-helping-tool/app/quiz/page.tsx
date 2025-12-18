"use client";

import { useState } from 'react';
import { generateQuiz, QuizQuestion } from '../../../services/studyMaterialService'; // Adjust path as needed
import QuizCard from '../../../components/quiz/QuizCard'; // Adjust path as needed

export default function QuizPage() {
  const [textToProcess, setTextToProcess] = useState('');
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateQuiz = async () => {
    setLoading(true);
    setError('');
    setQuestions([]);
    try {
      const response = await generateQuiz({ text: textToProcess });
      setQuestions(response.questions);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>Quiz Generator</h1>
      <p>Enter text below to generate a multiple-choice quiz.</p>

      <textarea
        value={textToProcess}
        onChange={(e) => setTextToProcess(e.target.value)}
        placeholder="Paste your study material here..."
        rows={15}
        style={{ width: '100%', padding: '10px', marginBottom: '20px', border: '1px solid #ccc', borderRadius: '4px' }}
      />

      <button
        onClick={handleGenerateQuiz}
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
        {loading ? 'Generating Quiz...' : 'Generate Quiz'}
      </button>

      {error && (
        <p style={{ color: 'red', marginTop: '20px' }}>Error: {error}</p>
      )}

      {questions.length > 0 && (
        <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h2>Generated Quiz</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
            {questions.map((q, index) => (
              <QuizCard key={index} question={q} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
