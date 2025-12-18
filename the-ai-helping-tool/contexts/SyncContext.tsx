// the-ai-helping-tool/contexts/SyncContext.tsx
import React,
{
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import {
  getUpdatedStudyMaterials,
  StudyMaterialResponse,
} from "../services/studyMaterialService";
import { useAuth } from "./AuthContext";

interface SyncContextType {
  lastSync: string | null;
  isSyncing: boolean;
  startSync: () => void;
  stopSync: () => void;
  updatedMaterials: StudyMaterialResponse[];
}

const SyncContext = createContext<SyncContextType | undefined>(undefined);

export const SyncProvider: React.FC = ({ children }) => {
  const { token } = useAuth();
  const [lastSync, setLastSync] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null);
  const [updatedMaterials, setUpdatedMaterials] = useState<
    StudyMaterialResponse[]
  >([]);

  const sync = useCallback(async () => {
    if (!token) return;

    try {
      const since = lastSync || new Date(0).toISOString();
      const materials = await getUpdatedStudyMaterials(since, token);
      if (materials.length > 0) {
        setUpdatedMaterials(materials);
      }
      setLastSync(new Date().toISOString());
    } catch (error) {
      console.error("Error during sync:", error);
    }
  }, [token, lastSync]);

  const startSync = useCallback(() => {
    if (isSyncing || !token) return;

    setIsSyncing(true);
    // Initial sync
    sync();
    // Set up polling
    const id = setInterval(sync, 30000); // 30 seconds
    setIntervalId(id);
  }, [isSyncing, token, sync]);

  const stopSync = useCallback(() => {
    if (!isSyncing || !intervalId) return;

    setIsSyncing(false);
    clearInterval(intervalId);
    setIntervalId(null);
  }, [isSyncing, intervalId]);

  useEffect(() => {
    return () => {
      // Clean up on unmount
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [intervalId]);

  return (
    <SyncContext.Provider
      value={{ lastSync, isSyncing, startSync, stopSync, updatedMaterials }}
    >
      {children}
    </SyncContext.Provider>
  );
};

export const useSync = () => {
  const context = useContext(SyncContext);
  if (!context) {
    throw new Error("useSync must be used within a SyncProvider");
  }
  return context;
};