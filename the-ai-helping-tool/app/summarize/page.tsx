"use client";

import { useState } from 'react';
import { summarizeText } from '../../../services/studyMaterialService'; // Adjust path as needed

export default function SummarizePage() {
  const [textToSummarize, setTextToSummarize] = useState('');
  const [detailLevel, setDetailLevel] = useState('normal');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    setSummary('');
    try {
      const response = await summarizeText({ text: textToSummarize, detail_level: detailLevel });
      setSummary(response.summary);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>Text Summarizer</h1>
      <p>Enter text below to generate a summary.</p>

      <textarea
        value={textToSummarize}
        onChange={(e) => setTextToSummarize(e.target.value)}
        placeholder="Paste your text here..."
        rows={15}
        style={{ width: '100%', padding: '10px', marginBottom: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
      />

      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="detailLevel" style={{ marginRight: '10px' }}>Detail Level:</label>
        <select
          id="detailLevel"
          value={detailLevel}
          onChange={(e) => setDetailLevel(e.target.value)}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="normal">Normal</option>
          <option value="brief">Brief</option>
        </select>
      </div>

      <button
        onClick={handleSummarize}
        disabled={loading || !textToSummarize.trim()}
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
        {loading ? 'Summarizing...' : 'Generate Summary'}
      </button>

      {error && (
        <p style={{ color: 'red', marginTop: '20px' }}>Error: {error}</p>
      )}

      {summary && (
        <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h2>Summary</h2>
          <div style={{ backgroundColor: '#f9f9f9', padding: '15px', borderRadius: '4px', border: '1px solid #eee', whiteSpace: 'pre-wrap' }}>
            {summary}
          </div>
        </div>
      )}
    </div>
  );
}
