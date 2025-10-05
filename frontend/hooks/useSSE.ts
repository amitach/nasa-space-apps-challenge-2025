/**
 * SSE Hook for real-time image updates
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface SSEImage {
  nasa_id: string;
  image_url: string;
  description: string;
  similarity_score: number;
  keywords: string[];
  category: string;
  query?: string; // Add query property for compatibility
}

export interface SSEImageEvent {
  query: string;
  images: SSEImage[];
  total: number;
  source?: 'tavus' | 'manual';
  timestamp?: number;
}

export interface SSEConnectionEvent {
  connection_id: string;
  status: string;
  message: string;
}

export function useSSE(url: string) {
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const [images, setImages] = useState<SSEImage[]>([]);
  const [lastQuery, setLastQuery] = useState<string>('');
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      return; // Already connected
    }

    const connId = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    console.log('🔌 Attempting SSE connection to:', url);
    const eventSource = new EventSource(`${url}?connection_id=${connId}`);

    eventSource.addEventListener('connected', (event) => {
      const data: SSEConnectionEvent = JSON.parse(event.data);
      console.log('✅ SSE Connected:', data);
      setConnectionId(data.connection_id);
      setConnected(true);
    });

    eventSource.addEventListener('images', (event) => {
      console.log('🎯 RAW SSE EVENT RECEIVED:', event);
      console.log('🎯 RAW EVENT DATA:', event.data);
      
      try {
        const data: SSEImageEvent = JSON.parse(event.data);
        console.log('='.repeat(80));
        console.log('📸 FRONTEND RECEIVED IMAGES VIA SSE');
        console.log('='.repeat(80));
        console.log(`🔍 Query: "${data.query}"`);
        console.log(`📊 Total images: ${data.total}`);
        console.log(`📡 Source: ${data.source}`);
        console.log(`🕐 Timestamp: ${new Date(data.timestamp * 1000).toLocaleTimeString()}`);
        console.log('📋 Images received:');
        console.log('📋 Full data object:', data);
        
        if (data.images && Array.isArray(data.images)) {
          data.images.forEach((img, index) => {
            console.log(`   ${index + 1}. ${img.nasa_id} - Score: ${img.similarity_score?.toFixed(3)} - ${img.description.substring(0, 50)}...`);
          });
          console.log('✅ Calling setImages with:', data.images);
          console.log('✅ Images array length:', data.images.length);
          console.log('✅ First image:', data.images[0]);
          setImages(data.images);
          setLastQuery(data.query);
          console.log('✅ setImages called successfully');
        } else {
          console.error('❌ Invalid images data:', data.images);
        }
        console.log('='.repeat(80));
      } catch (error) {
        console.error('❌ Error parsing SSE event data:', error);
        console.error('❌ Raw data:', event.data);
      }
    });

    eventSource.addEventListener('keepalive', () => {
      // Keepalive event, do nothing
    });

    eventSource.onopen = () => {
      console.log('✅ SSE Connection opened');
      console.log('✅ SSE Ready state:', eventSource.readyState);
      console.log('✅ SSE URL:', eventSource.url);
    };

    eventSource.onerror = (error) => {
      console.error('❌ SSE Error:', error);
      console.error('❌ SSE Error details:', {
        readyState: eventSource.readyState,
        url: eventSource.url,
        CONNECTING: eventSource.CONNECTING,
        OPEN: eventSource.OPEN,
        CLOSED: eventSource.CLOSED
      });
      
      if (eventSource.readyState === eventSource.CONNECTING) {
        console.log('🔄 SSE is still connecting...');
        return;
      }
      
      setConnected(false);
      eventSource.close();
      eventSourceRef.current = null;
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        console.log('🔄 Attempting to reconnect SSE...');
        connect();
      }, 3000);
    };

    eventSourceRef.current = eventSource;
  }, [url]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setConnected(false);
      setConnectionId(null);
      console.log('👋 SSE Disconnected');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connectionId,
    connected,
    images,
    lastQuery,
    connect,
    disconnect
  };
}
