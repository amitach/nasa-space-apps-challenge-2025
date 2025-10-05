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
    <div className="relative w-full h-full">
      {/* Background ISS image */}
      {backgroundImage && (
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${backgroundImage})` }}
        />
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
        style={{ mixBlendMode: 'normal' }}
      />
      
      {!isProcessing && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
          <p className="text-white">Loading video...</p>
        </div>
      )}
    </div>
  );
}
