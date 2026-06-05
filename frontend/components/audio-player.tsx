"use client";

/** AudioPlayer — Playback UI for recorded audio */
import { Play, Square, Trash2, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AudioPlayerProps {
  isRecording: boolean;
  audioBlob: Blob | null;
  duration: number;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onPlayRecording: () => void;
  onResetRecording: () => void;
}

export default function AudioPlayer({
  isRecording,
  audioBlob,
  duration,
  onStartRecording,
  onStopRecording,
  onPlayRecording,
  onResetRecording,
}: AudioPlayerProps) {
  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
      {!isRecording && !audioBlob && (
        <Button variant="outline" size="sm" onClick={onStartRecording} className="gap-1.5">
          <Mic className="w-3.5 h-3.5" />
          <span className="text-xs">Record</span>
        </Button>
      )}

      {isRecording && (
        <>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-xs font-medium text-red-500">{fmt(duration)}</span>
          </div>
          <Button variant="destructive" size="sm" onClick={onStopRecording} className="gap-1.5">
            <Square className="w-3.5 h-3.5" />
            <span className="text-xs">Stop</span>
          </Button>
        </>
      )}

      {!isRecording && audioBlob && (
        <>
          <Button variant="outline" size="sm" onClick={onPlayRecording} className="gap-1.5">
            <Play className="w-3.5 h-3.5" />
            <span className="text-xs">Play ({fmt(duration)})</span>
          </Button>
          <Button variant="ghost" size="icon" className="w-7 h-7" onClick={onResetRecording}>
            <Trash2 className="w-3.5 h-3.5 text-muted-foreground" />
          </Button>
        </>
      )}
    </div>
  );
}
