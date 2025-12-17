// the-ai-helping-tool/components/StudyMaterialList.tsx
import React, { useState, useEffect } from 'react';
import {
  getStudyMaterials,
  getUpdatedStudyMaterials,
  StudyMaterialResponse,
  StudyMaterialUpdate,
  updateStudyMaterial
} from '../services/studyMaterialService'; // Adjust path as needed

const POLLING_INTERVAL_MS = 5000; // Poll every 5 seconds for MVP

const StudyMaterialList: React.FC = () => {
  const [studyMaterials, setStudyMaterials] = useState<StudyMaterialResponse[]>([]);
  const [lastFetchedTimestamp, setLastFetchedTimestamp] = useState<string>(new Date().toISOString());
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingError, setPollingError] = useState<string | null>(null); // For polling specific errors

  // Function to fetch all study materials initially
  const fetchInitialStudyMaterials = async () => {
    try {
      setLoading(true);
      const materials = await getStudyMaterials();
      setStudyMaterials(materials);
      setLastFetchedTimestamp(new Date().toISOString());
    } catch (err) {
      setError(`Failed to fetch initial study materials: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Function to poll for updates
  const pollForUpdates = async () => {
    try {
      const updatedMaterials = await getUpdatedStudyMaterials(lastFetchedTimestamp);
      if (updatedMaterials.length > 0) {
        // Simple merge strategy: replace updated items, add new ones
        setStudyMaterials(prevMaterials => {
          const newMaterialsMap = new Map(prevMaterials.map(mat => [mat.id, mat]));
          updatedMaterials.forEach(updatedMat => {
            newMaterialsMap.set(updatedMat.id, updatedMat);
          });
          return Array.from(newMaterialsMap.values());
        });
        setLastFetchedTimestamp(new Date().toISOString());
        setPollingError(null); // Clear polling error on successful poll
      }
    } catch (err) {
      console.error('Error polling for study materials:', err);
      setPollingError(`Failed to get updates: ${err.message}`); // Set polling-specific error
    }
  };

  // Initial fetch on component mount
  useEffect(() => {
    fetchInitialStudyMaterials();
  }, []);

  // Set up polling interval
  useEffect(() => {
    const intervalId = setInterval(pollForUpdates, POLLING_INTERVAL_MS);

    // Clear interval on component unmount
    return () => clearInterval(intervalId);
  }, [lastFetchedTimestamp]); // Re-run effect if lastFetchedTimestamp changes (after an update)

  // Example handler for updating a material (e.g., changing processing status)
  const handleUpdateMaterial = async (id: number, data: StudyMaterialUpdate) => {
    try {
      const updatedMaterial = await updateStudyMaterial(id, data);
      setStudyMaterials(prevMaterials =>
        prevMaterials.map(mat => (mat.id === id ? updatedMaterial : mat))
      );
      // Update timestamp to ensure next poll reflects this change and avoids immediate re-fetch
      setLastFetchedTimestamp(new Date().toISOString()); 
    } catch (err) {
      setError(`Failed to update material: ${err.message}`);
    }
  };


  if (loading) return <div>Loading study materials...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>My Study Materials</h1>
      {pollingError && <div style={{ color: 'orange', marginBottom: '10px' }}>Polling Error: {pollingError}</div>} {/* Display polling error */}
      {studyMaterials.length === 0 ? (
        <p>No study materials uploaded yet. Upload one to get started!</p>
      ) : (
        <ul>
          {studyMaterials.map((material) => (
            <li key={material.id}>
              <strong>{material.file_name}</strong> (Status: {material.processing_status}) - Last Updated: {new Date(material.updated_at).toLocaleString()}
              {/* Example: A button to simulate updating status */}
              <button onClick={() => handleUpdateMaterial(material.id, { processing_status: 'processing' })}>
                Mark Processing
              </button>
              <button onClick={() => handleUpdateMaterial(material.id, { file_name: material.file_name + ' (renamed)' })}>
                Rename
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default StudyMaterialList;
