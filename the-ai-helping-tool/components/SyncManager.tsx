// the-ai-helping-tool/components/SyncManager.tsx
"use client";

import { useEffect } from 'react';
import { useSync } from '../contexts/SyncContext';

const SyncManager: React.FC = () => {
  const { startSync, stopSync } = useSync();

  useEffect(() => {
    startSync();
    return () => {
      stopSync();
    };
  }, [startSync, stopSync]);

  return null;
};

export default SyncManager;
