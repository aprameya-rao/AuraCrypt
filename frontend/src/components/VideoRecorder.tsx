import { useState, useRef, useEffect } from 'react';

interface Props {
  onRecordComplete: (blob: Blob) => void;
  disabled: boolean;
}

export default function VideoRecorder({ onRecordComplete, disabled }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecorded, setHasRecorded] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        setError("Camera access denied.");
      }
    };
    startCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!videoRef.current?.srcObject) return;

    chunksRef.current = [];
    const stream = videoRef.current.srcObject as MediaStream;
    const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
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
      <video ref={videoRef} autoPlay playsInline muted className={`media-feed ${isRecording ? 'recording' : ''}`} />
      
      {!isRecording ? (
        <button className="record-btn start" onClick={startRecording} disabled={disabled}>
          {hasRecorded ? 'RE-RECORD VIDEO' : 'RECORD VIDEO'}
        </button>
      ) : (
        <button className="record-btn stop" onClick={stopRecording}>
          STOP CAMERA
        </button>
      )}
      {hasRecorded && !isRecording && <div className="record-success">✓ Video captured</div>}
    </div>
  );
}