"use client";

import { AuthProvider } from "../contexts/AuthContext";
import { SyncProvider } from "../contexts/SyncContext";
import { SocketProvider } from "../contexts/SocketContext";
import SyncManager from "./SyncManager";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SyncProvider>
        <SocketProvider>
          <SyncManager />
          {children}
        </SocketProvider>
      </SyncProvider>
    </AuthProvider>
  );
}
