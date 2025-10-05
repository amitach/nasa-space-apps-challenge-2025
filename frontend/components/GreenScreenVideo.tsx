"use client";

import { useEffect, useRef, useState } from 'react';

interface GreenScreenVideoProps {
  videoTrack: MediaStreamTrack | null;
  backgroundImage?: string;
}

export default function GreenScreenVideo({ videoTrack, backgroundImage }: GreenScreenVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (!videoTrack || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    
    if (!ctx) return;

    // Set video stream
    video.srcObject = new MediaStream([videoTrack]);
    video.play().catch(err => {
      console.warn('Video autoplay failed:', err);
      // This is expected for autoplay policy, video will play once user interacts
    });

    let animationFrame: number;

    const processFrame = () => {
      if (!video.videoWidth || !video.videoHeight) {
        animationFrame = requestAnimationFrame(processFrame);
        return;
      }

      // Set canvas size to match video
      if (canvas.width !== video.videoWidth) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }

      // Draw video frame
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Apply improved chroma key (remove green screen with edge smoothing)
      const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const pixels = frame.data;

      // Tavus green screen RGB: [0, 255, 155]
      const targetR = 0;
      const targetG = 255;
      const targetB = 155;
      
      // First pass: Remove green and calculate alpha
      for (let i = 0; i < pixels.length; i += 4) {
        const r = pixels[i];
        const g = pixels[i + 1];
        const b = pixels[i + 2];

        // Calculate color distance from green screen
        const distance = Math.sqrt(
          Math.pow(r - targetR, 2) +
          Math.pow(g - targetG, 2) +
          Math.pow(b - targetB, 2)
        );

        // Threshold for full transparency (slightly higher for cleaner key)
        const threshold = 110;
        // Range for partial transparency (edge smoothing)
        const smoothRange = 60;

        if (distance < threshold) {
          // Full transparency for pure green
          pixels[i + 3] = 0;
        } else if (distance < threshold + smoothRange) {
          // Partial transparency for edges (smooth transition)
          const alpha = (distance - threshold) / smoothRange;
          pixels[i + 3] = Math.floor(pixels[i + 3] * alpha);
        }
      }
      
      // Second pass: Aggressive green spill removal on all visible pixels
      for (let i = 0; i < pixels.length; i += 4) {
        const alpha = pixels[i + 3];
        if (alpha > 0) {
          const r = pixels[i];
          const g = pixels[i + 1];
          const b = pixels[i + 2];
          
          // Remove green spill more aggressively
          if (g > r && g > b) {
            const maxOther = Math.max(r, b);
            const spillAmount = (g - maxOther) * 0.7; // More aggressive
            pixels[i + 1] = Math.max(maxOther, g - spillAmount);
          }
          
          // Edge feathering: slightly reduce alpha for pixels near edges
          if (alpha < 255 && alpha > 30) {
            pixels[i + 3] = Math.floor(alpha * 0.95);
          }
        }
      }

      ctx.putImageData(frame, 0, 0);
      animationFrame = requestAnimationFrame(processFrame);
    };

    video.onloadedmetadata = () => {
      setIsProcessing(true);
      processFrame();
    };

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
      setIsProcessing(false);
    };
  }, [videoTrack]);

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden">
      {/* Background ISS image with subtle overlay */}
      {backgroundImage && (
        <div className="absolute inset-0">
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${backgroundImage})` }}
          />
          {/* Subtle vignette effect */}
          <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/30"></div>
        </div>
      )}
      
      {/* Hidden video element */}
      <video
        ref={videoRef}
        className="hidden"
        autoPlay
        playsInline
        muted
      />
      
      {/* Canvas with transparent background (avatar only) */}
      <canvas
        ref={canvasRef}
        className="relative z-10 w-full h-full"
        style={{ 
          mixBlendMode: 'normal',
          filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5))'
        }}
      />
      
      {/* Loading state with modern design */}
      {!isProcessing && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900/90 to-blue-900/90 backdrop-blur-sm">
          <div className="text-center space-y-4">
            <div className="relative">
              <svg className="animate-spin h-16 w-16 mx-auto text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p className="text-white text-lg font-semibold">Loading video stream...</p>
            <p className="text-gray-300 text-sm">Please wait</p>
          </div>
        </div>
      )}
    </div>
  );
}
