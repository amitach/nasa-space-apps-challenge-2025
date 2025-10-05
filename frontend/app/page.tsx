"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { TavusClient } from '@/lib/tavus';
import { useSSE } from '@/hooks/useSSE';
import GreenScreenVideo from '@/components/GreenScreenVideo';

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
  const audioRef = useRef<HTMLAudioElement>(null);
  const [dailyCallFrame, setDailyCallFrame] = useState<any>(null);
  const [tavusConversation, setTavusConversation] = useState<TavusConversation | null>(null);
  const [tavusConnected, setTavusConnected] = useState(false);
  const [currentImages, setCurrentImages] = useState<ImageResult[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [sseConnected, setSseConnected] = useState(false);
  const [tavusClient, setTavusClient] = useState<TavusClient | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Image fetching state
  const [isFetchingImages, setIsFetchingImages] = useState(false);
  const [lastFetchQuery, setLastFetchQuery] = useState<string>('');
  const [fetchTimestamp, setFetchTimestamp] = useState<Date | null>(null);
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  
  // Green screen state
  const [replicaVideoTrack, setReplicaVideoTrack] = useState<MediaStreamTrack | null>(null);
  const [replicaAudioTrack, setReplicaAudioTrack] = useState<MediaStreamTrack | null>(null);
  const [audioBlocked, setAudioBlocked] = useState(false);
  const [useGreenScreen, setUseGreenScreen] = useState(true);
  const cupolaBackgroundUrl = '/cupola-bg.png';

  // Environment variables (NO SENSITIVE DATA!)
  const SSE_SERVER_URL = process.env.NEXT_PUBLIC_SSE_URL || 'http://localhost:5002/events';
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5002';

  // SSE connection
  const { connected: sseIsConnected, images: sseImages, lastQuery } = useSSE(SSE_SERVER_URL);
  
  // Debug sseImages state
  useEffect(() => {
    console.log('🔍 SSE IMAGES STATE CHANGED:', sseImages);
    console.log('🔍 SSE IMAGES LENGTH:', sseImages?.length);
    console.log('🔍 SSE CONNECTED:', sseIsConnected);
  }, [sseImages, sseIsConnected]);

  // Initialize on mount - no client-side API keys!
  useEffect(() => {
    setCurrentImages([]);
    setCurrentImageIndex(0);
    setTavusClient({} as any); // Placeholder, actual calls go through backend
    console.log('✅ Frontend initialized');
  }, []);

  // Handle SSE connection status
  useEffect(() => {
    setSseConnected(sseIsConnected);
  }, [sseIsConnected]);

  // Clear images when conversation ends (but not for test calls)
  // FIXED: Added a flag to prevent clearing during initial renders and only clear on actual disconnect
  const previousTavusConnectedRef = useRef(tavusConnected);
  
  // Track conversation state changes for debugging
  useEffect(() => {
    console.log('🔄 TAVUS CONNECTION STATE CHANGE:', {
      connected: tavusConnected,
      hasConversation: !!tavusConversation,
      conversationId: tavusConversation?.conversation_id,
      timestamp: new Date().toISOString()
    });
  }, [tavusConnected, tavusConversation]);
  
  useEffect(() => {
    // Only clear images if we were connected and now we're not (actual disconnect)
    const wasConnected = previousTavusConnectedRef.current;
    const isNowDisconnected = !tavusConnected;
    
    if (wasConnected && isNowDisconnected && currentImages.length > 0) {
      // Check if this is a test call by looking at the last query
      const isTestCall = lastQuery && lastQuery.includes('Cupola module');
      
      if (!isTestCall) {
        console.log('🧹 Clearing images - conversation actually ended');
        console.log('🧹 Previous state: connected =', wasConnected, ', Current state: connected =', tavusConnected);
        setCurrentImages([]);
        setCurrentImageIndex(0);
      } else {
        console.log('🧪 Keeping images - test call detected');
      }
    }
    
    // Update the ref for next render
    previousTavusConnectedRef.current = tavusConnected;
  }, [tavusConnected, currentImages.length, lastQuery]);

  // Handle SSE messages - show images when Tavus conversation is active OR when testing
  // FIXED: Only trigger when sseImages actually changes, prevent redundant renders
  const previousSseImagesRef = useRef<ImageResult[]>([]);
  
  useEffect(() => {
    // Only process if sseImages actually changed (by comparing length and first item)
    const hasChanged = 
      sseImages?.length !== previousSseImagesRef.current?.length ||
      sseImages?.[0]?.nasa_id !== previousSseImagesRef.current?.[0]?.nasa_id;
    
    if (!hasChanged) {
      console.log('⏭️ SSE images unchanged, skipping update');
      return;
    }
    
    console.log('🔍 SSE EFFECT TRIGGERED - sseImages changed');
    console.log('🔍 SSE EFFECT TRIGGERED - sseImages.length:', sseImages?.length);
    console.log('🔍 SSE EFFECT TRIGGERED - tavusConnected:', tavusConnected);
    
    if (sseImages && sseImages.length > 0) {
      console.log('='.repeat(80));
      console.log('🎯 FRONTEND PROCESSING IMAGES FOR DISPLAY');
      console.log('='.repeat(80));
      console.log(`✅ Tavus connected: ${tavusConnected}`);
      console.log(`📸 Images received: ${sseImages.length}`);
      console.log(`🔍 Query: "${lastQuery || 'Unknown'}"`);
      console.log('🖼️ Setting images for display...');
      
      // Clear fetching state and show success
      setIsFetchingImages(false);
      setShowSuccessNotification(true);
      
      // Hide success notification after 3 seconds
      setTimeout(() => {
        setShowSuccessNotification(false);
      }, 3000);
      
      setCurrentImages(sseImages);
      setCurrentImageIndex(0);
      console.log(`✅ Successfully updated UI with ${sseImages.length} images`);
      console.log('='.repeat(80));
      
      // Update the ref
      previousSseImagesRef.current = sseImages;
    } else {
      console.log('❌ No sseImages or empty array');
    }
  }, [sseImages, tavusConnected, lastQuery]);

  // Image slideshow
  useEffect(() => {
    if (currentImages.length <= 1) {
      // Only log if we have exactly 0 images (helpful for debugging)
      if (currentImages.length === 0) {
        console.log('🖼️ SLIDESHOW: No images to display');
      }
      return;
    }
    
    console.log('🖼️ SLIDESHOW: Starting slideshow with', currentImages.length, 'images');

    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % currentImages.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [currentImages]);

  // Play audio track when available
  useEffect(() => {
    if (replicaAudioTrack && audioRef.current) {
      console.log('🔊 Setting up audio track');
      const stream = new MediaStream([replicaAudioTrack]);
      audioRef.current.srcObject = stream;
      
      // Try to play audio - may fail due to browser autoplay policy
      audioRef.current.play().then(() => {
        console.log('✅ Audio playing successfully');
        setAudioBlocked(false);
      }).catch(err => {
        console.warn('⚠️ Audio autoplay blocked by browser. Click anywhere to enable audio.');
        console.warn('Error:', err);
        setAudioBlocked(true);
        
        // Add one-time click listener to enable audio
        const enableAudio = () => {
          if (audioRef.current) {
            audioRef.current.play().then(() => {
              console.log('✅ Audio enabled after user interaction');
              setAudioBlocked(false);
            }).catch(e => console.error('Failed to play audio:', e));
          }
          document.removeEventListener('click', enableAudio);
        };
        document.addEventListener('click', enableAudio);
      });
    }
  }, [replicaAudioTrack]);

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

  // Start Tavus conversation via backend
  const startConversation = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('🚀 Starting Tavus conversation via backend...');
      
      // Call backend to create conversation (secure)
      const response = await fetch(`${API_BASE_URL}/api/tavus-conversation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}) // Send empty JSON object
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || response.statusText;
        
        if (response.status === 400 && errorMessage.includes('concurrent')) {
          throw new Error('Too many active conversations. Please wait a moment and try again.');
        }
        
        throw new Error(`Failed to create conversation: ${errorMessage}`);
      }
      
      const conversation = await response.json();
      
      console.log('✅ Conversation created:', conversation);
      setTavusConversation(conversation);

      // Initialize Daily.co call (headless mode for custom video rendering)
      if (window.DailyIframe) {
        const callFrame = window.DailyIframe.createCallObject({});

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
        
        // Listen for when participants leave (including Tavus)
        callFrame.on('participant-left', (event: any) => {
          console.log('🚪 PARTICIPANT LEFT:', event);
          if (event.participant?.user_name?.includes('Tavus') || event.participant?.user_id?.includes('tavus')) {
            console.log('⚠️ Tavus participant left the call!');
          }
        });
        
        // Listen for call state changes
        callFrame.on('left-meeting', (event: any) => {
          console.log('🚪 LEFT MEETING:', event);
          console.log('⚠️ User or system left the Daily.co meeting');
          setTavusConnected(false);
        });
        
        // Listen for errors
        callFrame.on('error', (event: any) => {
          console.error('❌ DAILY.CO ERROR:', event);
        });
        
        // Listen for participant updates to extract video and audio tracks
        callFrame.on('participant-updated', (event: any) => {
          const participant = event.participant;
          if (!participant.local) {
            if (participant.tracks?.video?.state === 'playable') {
              console.log('🎥 Replica video track available');
              setReplicaVideoTrack(participant.tracks.video.persistentTrack);
            }
            if (participant.tracks?.audio?.state === 'playable') {
              console.log('🔊 Replica audio track available');
              setReplicaAudioTrack(participant.tracks.audio.persistentTrack);
            }
          }
        });
        
        // CRITICAL: Listen for Tavus tool calls via Daily.co app messages
        callFrame.on('app-message', async (event: any) => {
          console.log('📨 DAILY.CO APP MESSAGE RECEIVED:', event);
          
          try {
            const message = event.data;
            console.log('📋 Message data:', message);
            
            // Check if this is a tool call from Tavus
            if (message.message_type === 'conversation' && message.event_type === 'conversation.tool_call') {
              console.log('🔧 TAVUS TOOL CALL DETECTED!');
              console.log('🔧 Tool call details:', message.properties);
              console.log('🔧 Full message:', JSON.stringify(message, null, 2));
              
              const toolCall = message.properties;
              
              // Handle different possible structures for tool call data
              const toolName = toolCall?.tool_name || toolCall?.name || toolCall?.function?.name;
              
              // Tavus sends 'arguments' as a JSON string that needs parsing!
              let toolParams = toolCall?.tool_parameters || toolCall?.parameters || toolCall?.function?.parameters;
              
              // If arguments is a string, parse it
              if (toolCall?.arguments && typeof toolCall.arguments === 'string') {
                try {
                  toolParams = JSON.parse(toolCall.arguments);
                  console.log('✅ Parsed arguments from JSON string');
                } catch (e) {
                  console.error('❌ Failed to parse arguments:', e);
                }
              } else if (toolCall?.arguments && typeof toolCall.arguments === 'object') {
                toolParams = toolCall.arguments;
              }
              
              console.log('🔧 Extracted tool name:', toolName);
              console.log('🔧 Extracted tool params:', toolParams);
              
              if (toolName === 'fetch_relevant_image') {
                console.log('✅ Handling fetch_relevant_image tool call');
                
                // Set fetching state for UI feedback
                setIsFetchingImages(true);
                setLastFetchQuery(toolParams?.query || 'images');
                setFetchTimestamp(new Date());
                
                // Set timeout to clear loading if stuck (30 seconds)
                const timeoutId = setTimeout(() => {
                  console.warn('⚠️ Image fetch timeout - clearing loading state');
                  setIsFetchingImages(false);
                  setError('Image fetch timed out. Please try again.');
                }, 30000);
                
                try {
                  console.log('📤 Sending tool call to backend:', {
                    url: `${API_BASE_URL}/api/tavus-tool-call`,
                    tool_name: toolName,
                    query: toolParams?.query,
                    conversation_id: message.conversation_id
                  });
                  
                  // Call our tool call endpoint
                  const response = await fetch(`${API_BASE_URL}/api/tavus-tool-call`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      tool_name: toolName,
                      tool_params: toolParams,
                      conversation_id: message.conversation_id,
                      inference_id: message.properties?.inference_id
                    })
                  });
                  
                  console.log('📊 Backend response status:', response.status);
                  
                  if (!response.ok) {
                    throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
                  }
                  
                  const result = await response.json();
                  console.log('✅ Tool call result:', result);
                  
                  // Clear timeout since we got a response
                  clearTimeout(timeoutId);
                  
                  // Send the result back to Tavus via app message
                  if (result.tool_output) {
                    await callFrame.sendAppMessage({
                      message_type: 'conversation',
                      event_type: 'conversation.tool_call_result',
                      conversation_id: message.conversation_id,
                      properties: {
                        inference_id: message.properties.inference_id,
                        tool_call_id: message.properties.tool_call_id,
                        tool_output: result.tool_output
                      }
                    });
                    console.log('✅ Tool result sent back to Tavus');
                  }
                  
                } catch (toolError) {
                  console.error('❌ Tool call execution failed:', toolError);
                  
                  // Clear timeout and fetching state on error
                  clearTimeout(timeoutId);
                  setIsFetchingImages(false);
                  setError(`Failed to fetch images: ${toolError}`);
                  
                  // Send error back to Tavus
                  await callFrame.sendAppMessage({
                    message_type: 'conversation',
                    event_type: 'conversation.tool_call_result',
                    conversation_id: message.conversation_id,
                    properties: {
                      inference_id: message.properties.inference_id,
                      tool_call_id: message.properties.tool_call_id,
                      tool_output: {
                        status: 'error',
                        message: `Tool call failed: ${toolError}`
                      }
                    }
                  });
                }
              } else {
                console.warn('⚠️ Unknown tool call:', toolName);
                console.warn('⚠️ Available tool call data:', toolCall);
              }
            } else {
              console.log('📋 Non-tool-call app message:', message.event_type);
            }
          } catch (error) {
            console.error('❌ Error handling app message:', error);
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

    // Note: Tavus conversation automatically ends when Daily.co call ends
    // No need to explicitly call endConversation API since we're using backend-only credentials

    setTavusConversation(null);
    setTavusConnected(false);
    setCurrentImages([]);
    setCurrentImageIndex(0);
  }, [dailyCallFrame]);

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

  // Note: testTavusDirectToolCall removed - no longer needed with backend-only architecture
  // All Tavus API calls now go through secure backend endpoints

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
        {isFetchingImages && (
          <div className="px-4 py-2 rounded-lg bg-yellow-600 animate-pulse flex items-center gap-2">
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Fetching: {lastFetchQuery}</span>
          </div>
        )}
      </div>
      
      {/* Audio Blocked Notification */}
      {audioBlocked && tavusConnected && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-orange-600 text-white px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 z-50 cursor-pointer hover:bg-orange-700"
             onClick={() => {
               if (audioRef.current) {
                 audioRef.current.play().then(() => {
                   setAudioBlocked(false);
                 }).catch(e => console.error('Failed to play audio:', e));
               }
             }}>
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <div>
            <p className="font-semibold">🔊 Audio Muted</p>
            <p className="text-sm">Click here to enable audio</p>
          </div>
        </div>
      )}
      
      {/* Success Notification */}
      {showSuccessNotification && (
        <div className="fixed top-20 right-8 bg-green-600 text-white px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 animate-bounce z-50">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <div>
            <p className="font-semibold">✅ Images Loaded!</p>
            <p className="text-sm">{currentImages.length} images for "{lastQuery}"</p>
          </div>
        </div>
      )}

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
            
            {/* Video Display */}
            <div className="relative w-full h-96 bg-gray-900 rounded-lg mb-4 overflow-hidden" style={{ minHeight: '400px' }}>
              {useGreenScreen && replicaVideoTrack ? (
                <GreenScreenVideo 
                  videoTrack={replicaVideoTrack}
                  backgroundImage={cupolaBackgroundUrl}
                />
              ) : (
                <div 
                  ref={dailyFrameRef}
                  className="w-full h-full"
                />
              )}
              
              {!replicaVideoTrack && tavusConnected && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <svg className="animate-spin h-12 w-12 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p>Waiting for video...</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Green Screen Toggle */}
            <div className="mb-4 flex items-center gap-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useGreenScreen}
                  onChange={(e) => setUseGreenScreen(e.target.checked)}
                  className="w-4 h-4"
                />
                <span className="text-sm">Use Cupola Background</span>
              </label>
            </div>

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
                Test Tool Call
              </button>
            </div>
          </div>
        </div>

        {/* Image Display Section */}
        <div className="flex-1">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-semibold">ISS Images</h2>
              {lastQuery && currentImages.length > 0 && (
                <div className="text-sm text-gray-400">
                  Query: <span className="text-blue-400 font-mono">"{lastQuery}"</span>
                </div>
              )}
            </div>
            
            {/* Loading State */}
            {isFetchingImages && (
              <div className="bg-yellow-900 bg-opacity-30 border-2 border-yellow-600 rounded-lg p-6 mb-4">
                <div className="flex items-center gap-4">
                  <svg className="animate-spin h-8 w-8 text-yellow-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <div>
                    <p className="text-lg font-semibold text-yellow-400">🔍 Fetching Images...</p>
                    <p className="text-sm text-gray-300">Searching for: <span className="font-mono text-yellow-300">"{lastFetchQuery}"</span></p>
                    {fetchTimestamp && (
                      <p className="text-xs text-gray-400 mt-1">
                        Started: {fetchTimestamp.toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
            
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
      
      {/* Hidden audio element for Tavus audio */}
      <audio ref={audioRef} autoPlay playsInline style={{ display: 'none' }} />
    </div>
  );
}
