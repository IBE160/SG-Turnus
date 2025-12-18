"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: ReactNode;
  token: string | null; // Authentication token for WebSocket connection
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children, token }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!token) {
      console.warn("No authentication token provided for WebSocket connection.");
      if (socket) {
        socket.disconnect();
        setSocket(null);
      }
      return;
    }

    const newSocket = io(process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000', {
      path: '/ws/socket.io', // Match the path where Socket.IO is mounted on the backend
      query: { token },
      transports: ['websocket'], // Prefer WebSocket transport
    });

    newSocket.on('connect', () => {
      console.log('Socket.IO connected');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Socket.IO disconnected');
      setIsConnected(false);
    });

    newSocket.on('connect_error', (err) => {
      console.error('Socket.IO connection error:', err);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [token]); // Reconnect if token changes

  return (
    <SocketContext.Provider value={{ socket, isConnected }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
