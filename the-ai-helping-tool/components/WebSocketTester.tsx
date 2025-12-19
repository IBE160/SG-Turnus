"use client";

import React, { useEffect, useState } from 'react';
import { useSocket } from '../contexts/SocketContext'; // Adjust path as needed

interface StudyMaterial {
  id: number;
  file_name: string;
  // ... other fields from StudyMaterialResponse
}

const WebSocketTester: React.FC = () => {
  const { socket, isConnected } = useSocket();
  const [receivedMessages, setReceivedMessages] = useState<string[]>([]);

  useEffect(() => {
    if (socket) {
      console.log("WebSocketTester: Socket available, setting up listeners.");

      socket.on('study_material_created', (data: StudyMaterial) => {
        const message = `Study Material Created: ID=${data.id}, Name=${data.file_name}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      socket.on('study_material_updated', (data: StudyMaterial) => {
        const message = `Study Material Updated: ID=${data.id}, Name=${data.file_name}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      socket.on('study_material_deleted', (data: { id: number }) => {
        const message = `Study Material Deleted: ID=${data.id}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      socket.on('summary_created', (data: any) => { // Use 'any' or define a specific interface for summary
        const message = `Summary Created for SM ID: ${data.study_material_id}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      socket.on('flashcards_created', (data: any) => { // Use 'any' or define a specific interface for flashcards
        const message = `Flashcards Created for SM ID: ${data.study_material_id}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      socket.on('quiz_created', (data: any) => { // Use 'any' or define a specific interface for quiz
        const message = `Quiz Created for SM ID: ${data.study_material_id}`;
        setReceivedMessages((prev) => [...prev, message]);
        console.log(message, data);
      });

      return () => {
        console.log("WebSocketTester: Cleaning up socket listeners.");
        socket.off('study_material_created');
        socket.off('study_material_updated');
        socket.off('study_material_deleted');
        socket.off('summary_created');
        socket.off('flashcards_created');
        socket.off('quiz_created');
      };
    }
  }, [socket]);

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', margin: '20px', borderRadius: '8px' }}>
      <h3>WebSocket Tester</h3>
      <p>Connection Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      <div>
        <h4>Received Events:</h4>
        {receivedMessages.length === 0 ? (
          <p>No events received yet.</p>
        ) : (
          <ul>
            {receivedMessages.map((msg, index) => (
              <li key={index}>{msg}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default WebSocketTester;
