"use client";

import { useState, useEffect } from 'react';
import { summarizeText, exportSummary } from '../../services/studyMaterialService'; // Adjust path as needed

export default function SummarizePage() {
  const [textToSummarize, setTextToSummarize] = useState('');
  const [detailLevel, setDetailLevel] = useState('normal');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedSummary, setEditedSummary] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [isMobile, setIsMobile] = useState(false);
  const [exportFormat, setExportFormat] = useState('pdf');
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState('');

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    setSummary('');
    setIsEditing(false);
    setTags([]);
    try {
      const response = await summarizeText({ text: textToSummarize, detail_level: detailLevel });
      setSummary(response.summary);
      setEditedSummary(response.summary);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    setSummary(editedSummary);
    setIsEditing(false);
    // Here you would typically also make an API call to save the changes to the backend
  };

  const handleEdit = () => {
    setEditedSummary(summary);
    setIsEditing(true);
  }

  const handleCancel = () => {
    setIsEditing(false);
  }

  const handleEditButtonClick = () => {
    if (isEditing) {
      handleCancel();
    } else {
      handleEdit();
    }
  }

  const handleAddTag = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && event.currentTarget.value) {
      event.preventDefault();
      const newTag = event.currentTarget.value;
      setTags([...tags, newTag]);
      event.currentTarget.value = '';
      // Here you would typically also make an API call to save the new tag to the backend
    }
  };

  const handleExport = async () => {
    setExporting(true);
    setExportError('');
    try {
      const blob = await exportSummary({ content: summary, format: exportFormat });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `summary.${exportFormat}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setExportError(err.message || 'An unexpected error occurred during export.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <>
      <style jsx global>{`
        textarea::placeholder, input::placeholder {
          color: #6c757d;
          opacity: 1;
        }
      `}</style>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '2rem',
        backgroundColor: '#f0f2f5',
        minHeight: '100vh',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '1200px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          padding: '2rem'
        }}>
          <header style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#333' }}>
              AI Text Summarizer
            </h1>
            <p style={{ fontSize: '1.1rem', color: '#666' }}>
              Paste your text, choose the desired level of detail, and get a concise summary in seconds.
            </p>
          </header>

          <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr', gap: '2rem' }}>
            
            {/* Input Column */}
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <h2 style={{fontSize: '1.5rem', color: '#333', marginBottom: '1rem'}}>Your Text</h2>
              <textarea
                value={textToSummarize}
                onChange={(e) => setTextToSummarize(e.target.value)}
                placeholder="Paste your content here. The more text you provide, the better the summary will be..."
                rows={20}
                style={{
                  width: '100%',
                  padding: '1rem',
                  border: '1px solid #d9d9d9',
                  borderRadius: '4px',
                  fontSize: '1rem',
                  lineHeight: '1.5',
                  resize: 'vertical',
                  flexGrow: 1,
                }}
              />
            </div>

            {/* Output Column */}
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{fontSize: '1.5rem', color: '#333'}}>Summary</h2>
                {summary && !loading && (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={handleEditButtonClick}
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.9rem',
                        backgroundColor: isEditing ? '#ccc' : '#0070f3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                      aria-label={isEditing ? 'Cancel editing' : 'Edit summary'}
                    >
                      {isEditing ? 'Cancel' : 'Edit'}
                    </button>
                                         <select
                                          value={exportFormat}
                                          onChange={(e) => setExportFormat(e.target.value)}
                                          aria-label="Export format"
                                          style={{
                                            padding: '0.5rem',
                                            borderRadius: '4px',
                                            border: '1px solid #ccc',
                                          }}
                                        >                      <option value="pdf">PDF</option>
                      <option value="docx">DOCX</option>
                      <option value="csv">CSV</option>
                    </select>
                    <button
                      onClick={handleExport}
                      disabled={exporting}
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.9rem',
                        backgroundColor: '#17a2b8',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: exporting ? 'not-allowed' : 'pointer',
                      }}
                      aria-label="Export summary"
                    >
                      {exporting ? 'Exporting...' : 'Export'}
                    </button>
                  </div>
                )}
              </div>
              <div 
                style={{
                  flexGrow: 1,
                  padding: '1rem',
                  borderRadius: '4px',
                  backgroundColor: loading ? '#f0f2f5' : '#fff',
                  border: '1px solid #d9d9d9',
                  whiteSpace: 'pre-wrap',
                  overflowY: 'auto',
                  transition: 'background-color 0.3s'
                }}
                aria-live="polite"
              >
                {loading && <p role="status">Generating summary...</p>}
                {error && <p role="alert" style={{ color: 'red' }}>Error: {error}</p>}
                {exportError && <p role="alert" style={{ color: 'red' }}>Export Error: {exportError}</p>}
                {summary && !loading && (
                  isEditing ? (
                    <div>
                      <textarea
                        value={editedSummary}
                        onChange={(e) => setEditedSummary(e.target.value)}
                        rows={10}
                        style={{
                          width: '100%',
                          padding: '1rem',
                          border: '1px solid #d9d9d9',
                          borderRadius: '4px',
                          fontSize: '1rem',
                          lineHeight: '1.5',
                          resize: 'vertical',
                        }}
                        aria-label="Edit summary"
                      />
                      <button
                        onClick={handleSave}
                        style={{
                          marginTop: '1rem',
                          padding: '0.5rem 1rem',
                          fontSize: '0.9rem',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                        }}
                        aria-label="Save summary"
                      >
                        Save
                      </button>
                    </div>
                  ) : (
                    <p>{summary}</p>
                  )
                )}
                {!summary && !loading && !error && <p>Your summary will appear here.</p>}
              </div>
              {summary && !loading && (
                <div style={{ marginTop: '2rem' }}>
                  <h3 style={{ fontSize: '1.2rem', color: '#333', marginBottom: '1rem' }}>Tags</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                    {tags.map((tag, index) => (
                      <span key={index} style={{
                        backgroundColor: '#e0e0e0',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '16px',
                        fontSize: '0.9rem',
                      }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Add a tag and press Enter"
                    onKeyDown={handleAddTag}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                    }}
                  />
                </div>
              )}
            </div>
          </div>

          <footer style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            marginTop: '2rem',
            paddingTop: '2rem',
            borderTop: '1px solid #eee'
          }}>
            <div style={{ marginRight: '1.5rem' }}>
              <label htmlFor="detailLevel" style={{ marginRight: '0.5rem', fontSize: '1rem', color: '#333' }}>
                Detail Level:
              </label>
              <select
                id="detailLevel"
                value={detailLevel}
                onChange={(e) => setDetailLevel(e.target.value)}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontSize: '1rem'
                }}
              >
                <option value="normal">Normal</option>
                <option value="brief">Brief</option>
              </select>
            </div>

            <button
              onClick={handleSummarize}
              disabled={loading || !textToSummarize.trim()}
              style={{
                padding: '0.75rem 2rem',
                fontSize: '1.1rem',
                fontWeight: '600',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading || !textToSummarize.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !textToSummarize.trim() ? 0.6 : 1,
                transition: 'background-color 0.3s, opacity 0.3s',
              }}
              aria-label="Generate summary"
            >
              {loading ? 'Summarizing...' : 'Generate Summary'}
            </button>
          </footer>
        </div>
      </div>
    </>
  );
}