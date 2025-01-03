'use client';

import { useState, useRef, useEffect } from 'react';
import { PlayIcon, PauseIcon, StopIcon } from '@radix-ui/react-icons';
import { Button } from '@/components/ui/button';

export default function AudioPlayer({ audioBlob }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    // Create URL for the audio blob
    const url = URL.createObjectURL(audioBlob);
    setAudioUrl(url);

    // Cleanup function to revoke the URL when component unmounts
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [audioBlob]);

  const handlePlay = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  const handleError = (e) => {
    console.error('Audio playback error:', e);
    setIsPlaying(false);
  };

  if (!audioUrl) {
    return null;
  }

  return (
    <div className="flex items-center space-x-2">
      {isPlaying ? (
        <Button
          variant="ghost"
          size="icon"
          onClick={handlePause}
          title="Pause"
        >
          <PauseIcon className="h-4 w-4" />
        </Button>
      ) : (
        <Button
          variant="ghost"
          size="icon"
          onClick={handlePlay}
          title="Play"
        >
          <PlayIcon className="h-4 w-4" />
        </Button>
      )}
      <Button
        variant="ghost"
        size="icon"
        onClick={handleStop}
        title="Stop"
      >
        <StopIcon className="h-4 w-4" />
      </Button>
      <audio
        ref={audioRef}
        src={audioUrl}
        onEnded={handleEnded}
        onError={handleError}
        className="hidden"
      />
    </div>
  );
} 