import { useState, useRef, useEffect } from 'react';

interface Props {
  onRecordComplete: (blob: Blob) => void;
  disabled: boolean;
}

export default function AudioRecorder({ onRecordComplete, disabled }: Props) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecorded, setHasRecorded] = useState(false);
  const [error, setError] = useState('');

  // Only request mic when needed to prevent double prompts on page load
  const initAudio = async () => {
    if (streamRef.current) return true;
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
      return true;
    } catch (err) {
      setError("Microphone access denied.");
      return false;
    }
  };

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async (e: React.MouseEvent) => {
    e.preventDefault();
    const ready = await initAudio();
    if (!ready || !streamRef.current) return;

    chunksRef.current = [];
    const recorder = new MediaRecorder(streamRef.current); // Defaults to audio/webm or audio/ogg
    
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
      onRecordComplete(blob);
      setHasRecorded(true);
    };

    recorder.start();
    mediaRecorderRef.current = recorder;
    setIsRecording(true);
    setHasRecorded(false);
  };

  const stopRecording = (e: React.MouseEvent) => {
    e.preventDefault();
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  if (error) return <div className="recorder-error">{error}</div>;

  return (
    <div className="recorder-wrapper">
      <div className={`audio-status-box ${isRecording ? 'recording' : ''}`}>
        {isRecording ? "🔴 LISTENING..." : (hasRecorded ? "AUDIO SAVED" : "MIC STANDBY")}
      </div>
      
      {!isRecording ? (
        <button className="record-btn start" onClick={startRecording} disabled={disabled}>
          {hasRecorded ? 'RE-RECORD VOICE' : 'RECORD VOICE'}
        </button>
      ) : (
        <button className="record-btn stop" onClick={stopRecording}>
          STOP MIC
        </button>
      )}
      {hasRecorded && !isRecording && <div className="record-success">✓ Voice captured</div>}
    </div>
  );
}