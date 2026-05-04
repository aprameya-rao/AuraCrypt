import { useState } from 'react';

interface AuthProps {
  onSubmit: (username: string, pass: string, video: File, audio: File, isLogin: boolean) => void;
  isProcessing: boolean;
}

export default function SignUp({ onSubmit, isProcessing }: AuthProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (videoFile && audioFile) {
      onSubmit(username, password, videoFile, audioFile, false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-layout">
      <div className="form-header">
        <h2>New Enrollment</h2>
        <p>Register your 3-factor authentication</p>
      </div>

      <div className="input-group">
        <label htmlFor="signup-username">Choose Username</label>
        <input 
          id="signup-username"
          type="text" 
          required 
          value={username} 
          onChange={e => setUsername(e.target.value)} 
          disabled={isProcessing}
        />
      </div>

      <div className="input-group">
        <label htmlFor="signup-password">Choose Password</label>
        <input 
          id="signup-password"
          type="password" 
          required 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
          disabled={isProcessing}
        />
      </div>

      <div className="input-group">
        <label>Upload Face Video</label>
        <div className="file-input-wrapper">
          <input 
            type="file" 
            accept="video/*" 
            required 
            onChange={e => setVideoFile(e.target.files?.[0] || null)} 
            disabled={isProcessing}
          />
          <span className="file-name">{videoFile ? videoFile.name : 'No video selected'}</span>
        </div>
      </div>

      <div className="input-group">
        <label>Upload Voice Audio</label>
        <div className="file-input-wrapper">
          <input 
            type="file" 
            accept="audio/*" 
            required 
            onChange={e => setAudioFile(e.target.files?.[0] || null)} 
            disabled={isProcessing}
          />
          <span className="file-name">{audioFile ? audioFile.name : 'No audio selected'}</span>
        </div>
      </div>

      <button type="submit" disabled={isProcessing}>
        {isProcessing ? 'Processing...' : 'Enroll'}
      </button>
    </form>
  );
}