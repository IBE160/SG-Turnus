"use client";

import { useState } from 'react';
import { QuizQuestion } from '../../../services/studyMaterialService'; // Adjust path as needed

interface QuizCardProps {
  question: QuizQuestion;
}

export default function QuizCard({ question }: QuizCardProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);

  const handleAnswerSelection = (option: string) => {
    if (isAnswered) return;
    setSelectedAnswer(option);
    setIsAnswered(true);
  };

  const getOptionStyle = (option: string) => {
    if (!isAnswered) {
      return {
        border: '1px solid #ccc',
        backgroundColor: '#f9f9f9',
        cursor: 'pointer',
      };
    }

    const isCorrect = option === question.correct_answer;
    const isSelected = option === selectedAnswer;

    if (isCorrect) {
      return {
        border: '1px solid #28a745',
        backgroundColor: '#d4edda',
        cursor: 'default',
      };
    }

    if (isSelected) {
      return {
        border: '1px solid #dc3545',
        backgroundColor: '#f8d7da',
        cursor: 'default',
      };
    }

    return {
      border: '1px solid #ccc',
      backgroundColor: '#f9f9f9',
      cursor: 'default',
      opacity: 0.7,
    };
  };

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#fff', marginBottom: '20px' }}>
      <p style={{ fontWeight: 'bold', fontSize: '1.1em', marginBottom: '15px' }}>{question.question}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {question.options.map((option, index) => (
          <div
            key={index}
            onClick={() => handleAnswerSelection(option)}
            style={{
              padding: '12px',
              borderRadius: '5px',
              transition: 'background-color 0.3s, border-color 0.3s',
              ...getOptionStyle(option),
            }}
          >
            {option}
          </div>
        ))}
      </div>
      {isAnswered && (
        <div style={{ marginTop: '15px', paddingTop: '10px', borderTop: '1px solid #eee' }}>
          <p style={{ fontWeight: 'bold', color: selectedAnswer === question.correct_answer ? '#28a745' : '#dc3545' }}>
            {selectedAnswer === question.correct_answer
              ? 'Correct!'
              : `Incorrect. The correct answer is: ${question.correct_answer}`}
          </p>
        </div>
      )}
    </div>
  );
}
