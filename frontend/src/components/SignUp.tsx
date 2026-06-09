import { useState } from 'react';
import VideoRecorder from './VideoRecorder';
import AudioRecorder from './AudioRecorder';

interface AuthProps {
  onSubmit: (username: string, pass: string, videoBlob: Blob, audioBlob: Blob, isLogin: boolean) => void;
  isProcessing: boolean;
}

export default function SignUp({ onSubmit, isProcessing }: AuthProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (videoBlob && audioBlob) {
      onSubmit(username, password, videoBlob, audioBlob, false);
    } else {
      alert("Please record both video and voice biometrics.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-layout">
      <div className="form-header">
        <h2>New Enrollment</h2>
        <p>Register your 3-factor authentication live</p>
      </div>

      <div className="input-group">
        <label htmlFor="signup-username">Choose Username</label>
        <input 
          id="signup-username" type="text" required 
          value={username} onChange={e => setUsername(e.target.value)} 
          disabled={isProcessing}
        />
      </div>

      <div className="input-group">
        <label htmlFor="signup-password">Choose Password</label>
        <input 
          id="signup-password" type="password" required 
          value={password} onChange={e => setPassword(e.target.value)} 
          disabled={isProcessing}
        />
      </div>

      <div className="input-group">
        <label>Video Biometric</label>
        <VideoRecorder onRecordComplete={setVideoBlob} disabled={isProcessing} />
      </div>

      <div className="input-group">
        <label>Voice Biometric</label>
        <AudioRecorder onRecordComplete={setAudioBlob} disabled={isProcessing} />
      </div>

      <button type="submit" disabled={isProcessing || !videoBlob || !audioBlob}>
        {isProcessing ? 'Processing...' : 'Enroll'}
      </button>
    </form>
  );
}