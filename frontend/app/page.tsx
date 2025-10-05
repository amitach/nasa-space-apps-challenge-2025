"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { TavusClient } from '@/lib/tavus';
import { useSSE } from '@/hooks/useSSE';

// Daily.co type declarations
declare global {
  interface Window {
    DailyIframe: any;
  }
}

interface ImageResult {
  nasa_id: string;
  description: string;
  image_url: string;
  similarity_score: number;
  keywords: string[];
  category: string;
}

interface TavusConversation {
  conversation_id: string;
  conversation_url: string; // Changed from daily_room_url to conversation_url
  status: string;
  conversation_name?: string;
  callback_url?: string;
  created_at?: string;
}

export default function HomeCorrected() {
  const dailyFrameRef = useRef<HTMLDivElement>(null);
  const [dailyCallFrame, setDailyCallFrame] = useState<any>(null);
  const [tavusConversation, setTavusConversation] = useState<TavusConversation | null>(null);
  const [tavusConnected, setTavusConnected] = useState(false);
  const [currentImages, setCurrentImages] = useState<ImageResult[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [sseConnected, setSseConnected] = useState(false);
  const [tavusClient, setTavusClient] = useState<TavusClient | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Environment variables
  const TAVUS_API_KEY = process.env.NEXT_PUBLIC_TAVUS_API_KEY || '';
  const TAVUS_PERSONA_ID = process.env.NEXT_PUBLIC_TAVUS_PERSONA_ID || '';
  const TAVUS_REPLICA_ID = process.env.NEXT_PUBLIC_TAVUS_REPLICA_ID || '';
  const TAVUS_CALLBACK_URL = process.env.NEXT_PUBLIC_TAVUS_CALLBACK_URL || 'https://consulting-converter-insertion-maui.trycloudflare.com/api/tavus-webhook';
  const SSE_SERVER_URL = process.env.NEXT_PUBLIC_SSE_URL || 'https://cbf4f5efb944.ngrok-free.app/events';
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://cbf4f5efb944.ngrok-free.app';

  // SSE connection
  const { connected: sseIsConnected, images: sseImages, lastQuery } = useSSE(SSE_SERVER_URL);
  
  // Debug sseImages state
  useEffect(() => {
    console.log('🔍 SSE IMAGES STATE CHANGED:', sseImages);
    console.log('🔍 SSE IMAGES LENGTH:', sseImages?.length);
    console.log('🔍 SSE CONNECTED:', sseIsConnected);
  }, [sseImages, sseIsConnected]);

  // Initialize Tavus client and clear images on mount
  useEffect(() => {
    // Clear any existing images on page load
    setCurrentImages([]);
    setCurrentImageIndex(0);
    
        if (TAVUS_API_KEY && TAVUS_PERSONA_ID && TAVUS_REPLICA_ID) {
          const client = new TavusClient({
            apiKey: TAVUS_API_KEY,
            personaId: TAVUS_PERSONA_ID,
            replicaId: TAVUS_REPLICA_ID,
            callbackUrl: TAVUS_CALLBACK_URL
          });
      setTavusClient(client);
      console.log('✅ Tavus client initialized');
    } else {
      console.error('❌ Missing Tavus credentials');
      setError('Missing Tavus API credentials. Please check your environment variables.');
    }
  }, [TAVUS_API_KEY, TAVUS_PERSONA_ID, TAVUS_REPLICA_ID, TAVUS_CALLBACK_URL]);

  // Handle SSE connection status
  useEffect(() => {
    setSseConnected(sseIsConnected);
  }, [sseIsConnected]);

  // Clear images when conversation ends (but not for test calls)
  useEffect(() => {
    if (!tavusConnected && currentImages.length > 0) {
      // Check if this is a test call by looking at the last query
      const isTestCall = lastQuery && lastQuery.includes('Cupola module');
      
      if (!isTestCall) {
        console.log('🧹 Clearing images - conversation ended');
        setCurrentImages([]);
        setCurrentImageIndex(0);
      } else {
        console.log('🧪 Keeping images - test call detected');
      }
    }
  }, [tavusConnected, currentImages.length, lastQuery]);

  // Handle SSE messages - show images when Tavus conversation is active OR when testing
  useEffect(() => {
    console.log('🔍 SSE EFFECT TRIGGERED - sseImages:', sseImages);
    console.log('🔍 SSE EFFECT TRIGGERED - sseImages.length:', sseImages?.length);
    console.log('🔍 SSE EFFECT TRIGGERED - tavusConnected:', tavusConnected);
    
    if (sseImages && sseImages.length > 0) {
      // For now, always show images from SSE (we'll add proper source checking later)
      // TODO: Add proper source checking when we have access to the full SSE event data
      console.log('='.repeat(80));
      console.log('🎯 FRONTEND PROCESSING IMAGES FOR DISPLAY');
      console.log('='.repeat(80));
      console.log(`✅ Tavus connected: ${tavusConnected}`);
      console.log(`📸 Images received: ${sseImages.length}`);
      console.log(`🔍 Query: "${sseImages[0]?.query || 'Unknown'}"`);
      console.log('🖼️ Setting images for display...');
      console.log('🖼️ sseImages data:', sseImages);
      setCurrentImages(sseImages);
      setCurrentImageIndex(0);
      console.log(`✅ Successfully updated UI with ${sseImages.length} images`);
      console.log('='.repeat(80));
    } else {
      console.log('❌ No sseImages or empty array');
    }
  }, [sseImages, tavusConnected]);

  // Image slideshow
  useEffect(() => {
    console.log('🖼️ SLIDESHOW EFFECT - currentImages:', currentImages);
    console.log('🖼️ SLIDESHOW EFFECT - currentImages.length:', currentImages.length);
    
    if (currentImages.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % currentImages.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [currentImages]);

  // Load Daily.co script
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.DailyIframe) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/@daily-co/daily-js@latest/dist/daily-iframe.js';
      script.async = true;
      script.onload = () => {
        console.log('✅ Daily.co script loaded');
      };
      document.head.appendChild(script);
    }
  }, []);

  // Start Tavus conversation
  const startConversation = useCallback(async () => {
    if (!tavusClient) {
      setError('Tavus client not initialized');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log('🚀 Starting Tavus conversation...');
      const conversation = await tavusClient.createConversation();
      
      console.log('✅ Conversation created:', conversation);
      setTavusConversation(conversation);

      // Initialize Daily.co call
      if (window.DailyIframe && dailyFrameRef.current) {
        const callFrame = window.DailyIframe.createFrame(
          dailyFrameRef.current,
          {
            showLeaveButton: true,
            showFullscreenButton: true,
            showLocalVideo: true,
            showParticipantsBar: true,
            customTrayButtons: {
              'show-images': {
                iconPath: 'https://img.icons8.com/ios/50/000000/image.png',
                iconPathDarkMode: 'https://img.icons8.com/ios/50/ffffff/image.png',
                label: 'Show Images',
                tooltip: 'Display ISS images',
                visualState: 'default'
              }
            }
          }
        );

        // Join the Daily.co room
        await callFrame.join({ url: conversation.conversation_url });
        setDailyCallFrame(callFrame);
        setTavusConnected(true);
        
        // Add event listener for custom tray button
        callFrame.on('custom-button-click', (event: any) => {
          if (event.button_id === 'show-images') {
            // Trigger image search
            fetch(`${API_BASE_URL}/api/search`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ query: 'International Space Station', top_k: 5 })
            });
          }
        });
        
        console.log('✅ Joined Daily.co room');
      }

    } catch (error) {
      console.error('❌ Failed to start conversation:', error);
      setError(error instanceof Error ? error.message : 'Failed to start conversation');
    } finally {
      setIsLoading(false);
    }
  }, [tavusClient]);

  // End conversation
  const endConversation = useCallback(async () => {
    if (dailyCallFrame) {
      await dailyCallFrame.destroy();
      setDailyCallFrame(null);
    }

    if (tavusConversation && tavusClient) {
      try {
        await tavusClient.endConversation(tavusConversation.conversation_id);
      } catch (error) {
        console.error('Error ending conversation:', error);
      }
    }

    setTavusConversation(null);
    setTavusConnected(false);
    setCurrentImages([]);
    setCurrentImageIndex(0);
  }, [dailyCallFrame, tavusConversation, tavusClient]);

  // Test SSE connection
  const testSSE = useCallback(async () => {
    try {
      await fetch(`${API_BASE_URL}/api/test-sse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Hello from frontend!' })
      });
    } catch (error) {
      console.error('Failed to test SSE:', error);
    }
  }, [API_BASE_URL]);

  // Test image search - only works when conversation is active
  const testImageSearch = useCallback(async () => {
    if (!tavusConnected) {
      console.log('❌ Cannot test image search - no active conversation');
      setError('Please start a conversation first before testing image search');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'Cupola module', top_k: 5 })
      });
      
      const data = await response.json();
      console.log('🔍 Image search response:', data);
      
      if (data.success && data.data.images) {
        setCurrentImages(data.data.images);
        setCurrentImageIndex(0);
        console.log(`🖼️ Loaded ${data.data.images.length} images directly`);
      }
    } catch (error) {
      console.error('Failed to test image search:', error);
    }
  }, [tavusConnected, API_BASE_URL]);

      // Test Tavus tool call endpoint (simulates what Tavus sends to us)
      const testTavusToolCall = useCallback(async () => {
        console.log('🧪 TESTING TAVUS TOOL CALL ENDPOINT (what Tavus sends to us)');
        try {
          const response = await fetch(`${API_BASE_URL}/api/tavus-tool-call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              type: 'tool_call',
              tool_call: {
                name: 'fetch_relevant_image',
                parameters: {
                  query: 'International Space Station Cupola module',
                  top_k: 3
                }
              }
            })
          });
          
          const data = await response.json();
          console.log('🧪 Tavus tool call test response:', data);
        } catch (error) {
          console.error('Failed to test Tavus tool call:', error);
        }
      }, [API_BASE_URL]);

  // Test Tavus direct tool call (simulates what we send to Tavus)
  const testTavusDirectToolCall = useCallback(async () => {
    console.log('🧪 TESTING TAVUS DIRECT TOOL CALL (what we send to Tavus)');
    try {
      if (tavusClient) {
        const result = await tavusClient.callTool('fetch_relevant_image', {
          query: 'Cupola module',
          top_k: 3
        });
        console.log('🧪 Tavus direct tool call test response:', result);
      } else {
        console.error('❌ Tavus client not initialized');
      }
    } catch (error) {
      console.error('Failed to test Tavus direct tool call:', error);
    }
  }, [tavusClient]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex flex-col items-center justify-center p-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">🚀 ISS Explorer</h1>
        <p className="text-gray-300">AI-powered video chat with real-time image display</p>
      </div>

      {/* Status Indicators */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className={`px-4 py-2 rounded-lg ${sseConnected ? 'bg-green-600' : 'bg-red-600'}`}>
          SSE: {sseConnected ? 'Connected' : 'Disconnected'}
        </div>
        <div className={`px-4 py-2 rounded-lg ${tavusConnected ? 'bg-green-600' : 'bg-gray-600'}`}>
          Tavus: {tavusConnected ? 'Connected' : 'Disconnected'}
        </div>
        <div className={`px-4 py-2 rounded-lg ${currentImages.length > 0 ? 'bg-blue-600' : 'bg-gray-600'}`}>
          Images: {currentImages.length}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-600 text-white p-4 rounded-lg mb-6 max-w-md">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-8 w-full max-w-7xl">
        {/* Video Chat Section */}
        <div className="flex-1">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Video Chat</h2>
            
            {/* Daily.co Frame */}
            <div 
              ref={dailyFrameRef}
              className="w-full h-96 bg-gray-700 rounded-lg mb-4"
              style={{ minHeight: '400px' }}
            />

            {/* Controls */}
            <div className="flex flex-wrap gap-2">
              {!tavusConnected ? (
                <button
                  onClick={startConversation}
                  disabled={isLoading || !tavusClient}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-semibold"
                >
                  {isLoading ? 'Starting...' : 'Start Conversation'}
                </button>
              ) : (
                <button
                  onClick={endConversation}
                  className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-semibold"
                >
                  End Conversation
                </button>
              )}

              <button
                onClick={testSSE}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
              >
                Test SSE
              </button>

              <button
                onClick={testImageSearch}
                disabled={!tavusConnected}
                className={`px-4 py-2 rounded-lg ${
                  tavusConnected 
                    ? 'bg-purple-600 hover:bg-purple-700' 
                    : 'bg-gray-600 cursor-not-allowed'
                }`}
              >
                Test Images
              </button>

                  <button
                    onClick={testTavusToolCall}
                    className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg"
                  >
                    Test Tavus Tool Call
                  </button>

                  <button
                    onClick={testTavusDirectToolCall}
                    className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg"
                  >
                    Test Tavus Direct Tool Call
                  </button>
            </div>
          </div>
        </div>

        {/* Image Display Section */}
        <div className="flex-1">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">ISS Images</h2>
            
            {currentImages.length > 0 ? (
              <div className="space-y-4">
                {/* Current Image */}
                <div className="relative">
                  <img
                    src={currentImages[currentImageIndex]?.image_url}
                    alt={currentImages[currentImageIndex]?.description}
                    className="w-full h-64 object-cover rounded-lg"
                    onError={(e) => {
                      console.error('Image failed to load:', e);
                      e.currentTarget.src = '/placeholder-image.jpg';
                    }}
                  />
                  
                  {/* Image Navigation */}
                  {currentImages.length > 1 && (
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                      <button
                        onClick={() => setCurrentImageIndex((prev) => (prev - 1 + currentImages.length) % currentImages.length)}
                        className="px-3 py-1 bg-black bg-opacity-50 rounded text-white"
                      >
                        ←
                      </button>
                      <span className="px-3 py-1 bg-black bg-opacity-50 rounded text-white">
                        {currentImageIndex + 1} / {currentImages.length}
                      </span>
                      <button
                        onClick={() => setCurrentImageIndex((prev) => (prev + 1) % currentImages.length)}
                        className="px-3 py-1 bg-black bg-opacity-50 rounded text-white"
                      >
                        →
                      </button>
                    </div>
                  )}
                </div>

                {/* Image Info */}
                <div className="text-sm text-gray-300">
                  <p className="font-semibold">Description:</p>
                  <p>{currentImages[currentImageIndex]?.description}</p>
                  
                  <p className="font-semibold mt-2">Keywords:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {currentImages[currentImageIndex]?.keywords?.map((keyword, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-600 rounded text-xs">
                        {keyword}
                      </span>
                    ))}
                  </div>
                  
                  <p className="font-semibold mt-2">Similarity Score:</p>
                  <p>{currentImages[currentImageIndex]?.similarity_score?.toFixed(3)}</p>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-400 py-8">
                {tavusConnected ? (
                  <>
                    <p>No images loaded yet.</p>
                    <p className="text-sm mt-2">Ask the AI to show you images or use the test button!</p>
                  </>
                ) : (
                  <>
                    <p>No active conversation.</p>
                    <p className="text-sm mt-2">Start a conversation to see images or test the webhook!</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-gray-400 text-sm">
        <p>ISS Explorer - NASA Space Apps Challenge 2025</p>
        <p>Powered by Tavus AI, Daily.co, and NASA Image API</p>
      </div>
    </div>
  );
}
