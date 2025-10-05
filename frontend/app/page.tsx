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
  const [tavusClient, setTavusClient] = useState<TavusClient | null>({} as any); // Initialize immediately since backend handles auth
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
    <div className="h-screen bg-slate-950 text-white flex flex-col relative overflow-hidden">
      {/* Subtle grid background */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: 'linear-gradient(rgba(100, 100, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(100, 100, 255, 0.1) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>
      
      {/* Header Bar */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-sm relative z-50">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-xl font-bold tracking-widest text-white">ISS EXPLORER</h1>
              <p className="text-[10px] text-gray-500 font-mono tracking-wider uppercase">Mission Control Interface</p>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex gap-3">
            <div className={`px-3 py-1.5 rounded border font-mono text-[10px] tracking-wider transition-all duration-200 ${
              sseConnected 
                ? 'bg-green-950/30 border-green-500/50 text-green-400' 
                : 'bg-red-950/30 border-red-500/50 text-red-400'
            }`}>
              <span className="flex items-center gap-1.5">
                <span className={`w-1 h-1 rounded-full ${sseConnected ? 'bg-green-400' : 'bg-red-400'}`}></span>
                SSE
              </span>
            </div>
            <div className={`px-3 py-1.5 rounded border font-mono text-[10px] tracking-wider transition-all duration-200 ${
              tavusConnected 
                ? 'bg-blue-950/30 border-blue-500/50 text-blue-400' 
                : 'bg-gray-800/50 border-gray-600/50 text-gray-400'
            }`}>
              <span className="flex items-center gap-1.5">
                <span className={`w-1 h-1 rounded-full ${tavusConnected ? 'bg-blue-400' : 'bg-gray-500'}`}></span>
                TAVUS
              </span>
            </div>
            <div className={`px-3 py-1.5 rounded border font-mono text-[10px] tracking-wider transition-all duration-200 ${
              currentImages.length > 0 
                ? 'bg-purple-950/30 border-purple-500/50 text-purple-400' 
                : 'bg-gray-800/50 border-gray-600/50 text-gray-400'
            }`}>
              IMG: {currentImages.length}
            </div>
            {isFetchingImages && (
              <div className="px-3 py-1.5 rounded border border-yellow-500/50 bg-yellow-950/30 flex items-center gap-1.5 font-mono text-[10px] tracking-wider text-yellow-400">
                <svg className="animate-spin h-2.5 w-2.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                FETCH
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Audio Blocked Notification */}
      {audioBlocked && tavusConnected && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-orange-950/90 text-white px-4 py-2 rounded border border-orange-500/50 flex items-center gap-2 z-50 cursor-pointer backdrop-blur-xl"
             onClick={() => {
               if (audioRef.current) {
                 audioRef.current.play().then(() => {
                   setAudioBlocked(false);
                 }).catch(e => console.error('Failed to play audio:', e));
               }
             }}>
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <p className="text-xs font-mono">AUDIO MUTED - CLICK TO ENABLE</p>
        </div>
      )}
      
      {/* Success Notification */}
      {showSuccessNotification && (
        <div className="fixed top-20 right-6 bg-green-950/90 text-white px-4 py-2 rounded border border-green-500/50 flex items-center gap-2 z-50 backdrop-blur-xl">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <p className="text-xs font-mono">{currentImages.length} IMAGES LOADED</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 bg-red-950/90 text-white px-4 py-2 rounded border border-red-500/50 backdrop-blur-xl z-50 max-w-md">
          <p className="text-xs font-mono">ERROR: {error}</p>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex relative">
        {/* Video Section - Full Width/Height */}
        <div className={`flex-1 flex flex-col transition-all duration-500 ease-out ${
          currentImages.length > 0 ? 'mr-0' : ''
        }`}>
          {/* Video Display - Calculate height to leave room for controls */}
          <div className="relative bg-black z-10" style={{ height: 'calc(100vh - 57px - 80px)' }}>
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
              <div className="absolute inset-0 flex items-center justify-center text-gray-400 bg-slate-900/50">
                <div className="text-center">
                  <svg className="animate-spin h-12 w-12 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-xs font-mono tracking-wider">ESTABLISHING CONNECTION</p>
                </div>
              </div>
            )}
            
            {!tavusConnected && (
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-black">
                <div className="text-center space-y-8">
                  <div className="relative">
                    <div className="w-24 h-24 mx-auto border-2 border-gray-700 rounded-lg flex items-center justify-center">
                      <div className="w-16 h-16 border border-gray-600 rounded"></div>
                    </div>
                  </div>
                  <div>
                    <p className="text-base font-mono tracking-widest text-gray-500">SYSTEM STANDBY</p>
                    <p className="text-xs font-mono text-gray-600 mt-2">Awaiting Session Initiation</p>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Bottom Control Bar */}
          <div className="border-t border-gray-800 bg-black/95 backdrop-blur-md relative z-50">
            <div className="px-8 py-4 flex items-center justify-between">
              <div className="flex items-center gap-8">
                {/* Green Screen Toggle */}
                <label className="flex items-center gap-2.5 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={useGreenScreen}
                    onChange={(e) => setUseGreenScreen(e.target.checked)}
                    className="w-4 h-4 accent-blue-500 cursor-pointer"
                  />
                  <span className="text-xs font-mono tracking-wider text-gray-400 group-hover:text-gray-300 transition-colors">CUPOLA BACKGROUND</span>
                </label>
                
                {/* Session Info */}
                {tavusConnected && (
                  <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                    <span>LIVE SESSION</span>
                  </div>
                )}
              </div>
              
              {/* Controls */}
              <div className="flex items-center gap-3">
                {!tavusConnected ? (
                  <button
                    onClick={startConversation}
                    disabled={isLoading || !tavusClient}
                    className="px-10 py-2.5 bg-blue-600/30 hover:bg-blue-600/40 disabled:bg-gray-800 disabled:cursor-not-allowed border border-blue-500/70 disabled:border-gray-700 rounded font-mono text-sm tracking-widest text-blue-300 hover:text-blue-200 disabled:text-gray-600 transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30"
                  >
                    {isLoading ? 'STARTING...' : 'START SESSION'}
                  </button>
                ) : (
                  <button
                    onClick={endConversation}
                    className="px-10 py-2.5 bg-red-600/30 hover:bg-red-600/40 border border-red-500/70 rounded font-mono text-sm tracking-widest text-red-300 hover:text-red-200 transition-all duration-200 shadow-lg shadow-red-500/20 hover:shadow-red-500/30"
                  >
                    END SESSION
                  </button>
                )}
                
                <div className="w-px h-8 bg-gray-800"></div>
                
                {/* Emergency Reset - Always visible */}
                {(tavusConnected || dailyCallFrame || tavusConversation) && (
                  <button
                    onClick={() => {
                      // Force reset everything
                      if (dailyCallFrame) {
                        dailyCallFrame.destroy().catch(() => {});
                        setDailyCallFrame(null);
                      }
                      setTavusConversation(null);
                      setTavusConnected(false);
                      setReplicaVideoTrack(null);
                      setReplicaAudioTrack(null);
                      setCurrentImages([]);
                      setCurrentImageIndex(0);
                      console.log('🔄 Emergency reset triggered');
                    }}
                    className="px-5 py-2.5 bg-gray-700/20 hover:bg-gray-700/40 border border-gray-600/40 hover:border-gray-600/60 rounded font-mono text-xs tracking-wider text-gray-400 hover:text-gray-300 transition-all duration-200"
                    title="Force reset session"
                  >
                    RESET
                  </button>
                )}

                <button
                  onClick={testSSE}
                  className="px-5 py-2.5 bg-green-600/10 hover:bg-green-600/20 border border-green-500/30 hover:border-green-500/50 rounded font-mono text-xs tracking-wider text-green-400 hover:text-green-300 transition-all duration-200"
                >
                  SSE
                </button>

                <button
                  onClick={testImageSearch}
                  disabled={!tavusConnected}
                  className={`px-5 py-2.5 border rounded font-mono text-xs tracking-wider transition-all duration-200 ${
                    tavusConnected 
                      ? 'bg-purple-600/10 hover:bg-purple-600/20 border-purple-500/30 hover:border-purple-500/50 text-purple-400 hover:text-purple-300' 
                      : 'bg-gray-800/30 border-gray-700/40 text-gray-600 cursor-not-allowed'
                  }`}
                >
                  IMG
                </button>

                <button
                  onClick={testTavusToolCall}
                  className="px-5 py-2.5 bg-orange-600/10 hover:bg-orange-600/20 border border-orange-500/30 hover:border-orange-500/50 rounded font-mono text-xs tracking-wider text-orange-400 hover:text-orange-300 transition-all duration-200"
                >
                  TOOL
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sliding Image Panel - Only visible when images exist */}
        <div className={`fixed right-0 top-[57px] bottom-0 w-[450px] bg-black/95 backdrop-blur-xl border-l border-gray-800 transition-transform duration-500 ease-out z-40 ${
          currentImages.length > 0 ? 'translate-x-0' : 'translate-x-full'
        }`}>
          <div className="h-full flex flex-col">
            {/* Panel Header */}
            <div className="border-b border-gray-800 px-4 py-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold tracking-wider text-gray-200 font-mono">IMAGE DATABASE</h2>
                {lastQuery && (
                  <p className="text-[10px] text-gray-500 font-mono mt-0.5">QUERY: {lastQuery}</p>
                )}
              </div>
              <button
                onClick={() => {
                  setCurrentImages([]);
                  setCurrentImageIndex(0);
                }}
                className="text-gray-500 hover:text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Loading State */}
            {isFetchingImages && (
              <div className="px-4 py-3 border-b border-gray-800 bg-yellow-950/10">
                <div className="flex items-center gap-2">
                  <svg className="animate-spin h-3 w-3 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <p className="text-xs font-mono tracking-wider text-yellow-400">FETCHING...</p>
                </div>
              </div>
            )}
            
            {/* Image Content */}
            <div className="flex-1 overflow-y-auto">
              {currentImages.length > 0 && (
                <div className="p-4 space-y-4">
                  {/* Current Image */}
                  <div className="relative">
                    <img
                      src={currentImages[currentImageIndex]?.image_url}
                      alt={currentImages[currentImageIndex]?.description}
                      className="w-full aspect-video object-cover rounded border border-gray-800"
                      onError={(e) => {
                        console.error('Image failed to load:', e);
                        e.currentTarget.src = '/placeholder-image.jpg';
                      }}
                    />
                  </div>
                  
                  {/* Image Navigation */}
                  {currentImages.length > 1 && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => setCurrentImageIndex((prev) => (prev - 1 + currentImages.length) % currentImages.length)}
                        className="flex-1 px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-white text-xs font-mono transition-colors"
                      >
                        PREV
                      </button>
                      <span className="px-4 py-1.5 bg-gray-900 border border-gray-700 rounded text-white text-xs font-mono">
                        {currentImageIndex + 1}/{currentImages.length}
                      </span>
                      <button
                        onClick={() => setCurrentImageIndex((prev) => (prev + 1) % currentImages.length)}
                        className="flex-1 px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded text-white text-xs font-mono transition-colors"
                      >
                        NEXT
                      </button>
                    </div>
                  )}

                  {/* Image Info */}
                  <div className="space-y-3">
                    <div>
                      <p className="text-[10px] font-mono tracking-wider text-gray-500 mb-1.5">DESCRIPTION</p>
                      <p className="text-xs text-gray-300 leading-relaxed">{currentImages[currentImageIndex]?.description}</p>
                    </div>
                    
                    <div>
                      <p className="text-[10px] font-mono tracking-wider text-gray-500 mb-1.5">KEYWORDS</p>
                      <div className="flex flex-wrap gap-1">
                        {currentImages[currentImageIndex]?.keywords?.map((keyword, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-blue-600/20 border border-blue-500/50 rounded text-[10px] font-mono text-blue-400">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-[10px] font-mono tracking-wider text-gray-500 mb-1">SIMILARITY</p>
                        <p className="text-base font-mono font-bold text-green-400">{currentImages[currentImageIndex]?.similarity_score?.toFixed(3)}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-mono tracking-wider text-gray-500 mb-1">NASA ID</p>
                        <p className="text-[10px] font-mono text-gray-400 break-all">{currentImages[currentImageIndex]?.nasa_id}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Hidden audio element for Tavus audio */}
      <audio ref={audioRef} autoPlay playsInline style={{ display: 'none' }} />
    </div>
  );
}
