import { useState } from 'react';
import VideoRecorder from './VideoRecorder';
import AudioRecorder from './AudioRecorder';

interface AuthProps {
  onSubmit: (username: string, pass: string, videoBlob: Blob, audioBlob: Blob, isLogin: boolean) => void;
  isProcessing: boolean;
}

export default function Login({ onSubmit, isProcessing }: AuthProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (videoBlob && audioBlob) {
      onSubmit(username, password, videoBlob, audioBlob, true);
    } else {
      alert("Please record both video and voice biometrics.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-layout">
      <div className="form-header">
        <h2>Access Portal</h2>
        <p>Authenticate with your live biometrics</p>
      </div>

      <div className="input-group">
        <label htmlFor="login-username">Username</label>
        <input 
          id="login-username" type="text" required 
          value={username} onChange={e => setUsername(e.target.value)} 
          disabled={isProcessing}
        />
      </div>

      <div className="input-group">
        <label htmlFor="login-password">Password</label>
        <input 
          id="login-password" type="password" required 
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
        {isProcessing ? 'Authenticating...' : 'Login'}
      </button>
    </form>
  );
}