import { useState, useRef, useEffect } from 'react';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';
import Login from './components/Login';
import SignUp from './components/SignUp';
import { loginUser, enrollUser } from './api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [isReady, setIsReady] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState({ message: '', type: '' });

  const ffmpegRef = useRef(new FFmpeg());

  useEffect(() => {
    const loadFFmpeg = async () => {
      try {
        const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm';
        const ffmpeg = ffmpegRef.current;
        await ffmpeg.load({
          coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
          wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
        });
        setIsReady(true);
      } catch (error) {
        console.error("Failed to load FFmpeg:", error);
        setStatus({ message: "Failed to initialize media engine. Check network.", type: "error" });
      }
    };
    loadFFmpeg();
  }, []);

  // Reusable converter for both audio and video blobs
  const convertMediaBlob = async (blob: Blob, outputName: string, outputMime: string): Promise<File> => {
    const ffmpeg = ffmpegRef.current;
    const inputName = `input_${outputName}.webm`;
    
    await ffmpeg.writeFile(inputName, await fetchFile(blob));
    await ffmpeg.exec(['-i', inputName, outputName]);
    const data = await ffmpeg.readFile(outputName);
    
    return new File([new Blob([data], { type: outputMime })], outputName, { type: outputMime });
  };

  const handleAuth = async (username: string, pass: string, videoBlob: Blob, audioBlob: Blob, isLogin: boolean) => {
    setIsProcessing(true);
    setStatus({ message: "Transcoding media to secure formats...", type: "info" });

    try {
      // Convert the separate blobs to the exact formats your backend expects
      const finalVideo = await convertMediaBlob(videoBlob, 'video.mp4', 'video/mp4');
      const finalAudio = await convertMediaBlob(audioBlob, 'audio.wav', 'audio/wav');

      setStatus({ message: "Connecting to server...", type: "info" });

      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', pass);
      formData.append('video_file', finalVideo);
      formData.append('audio_file', finalAudio);

      if (isLogin) {
        await loginUser(formData);
        setStatus({ message: "Login Successful.", type: "success" });
      } else {
        await enrollUser(formData);
        setStatus({ message: "Enrollment Successful.", type: "success" });
      }

    } catch (error: any) {
      console.error("Processing/API error:", error);
      setStatus({ message: `Failed: ${error.message || "An unexpected error occurred."}`, type: "error" });
    } finally {
      setIsProcessing(false);
    }
  };

  const switchTab = (tab: 'login' | 'signup') => {
    if (isProcessing) return; 
    setActiveTab(tab);
    setStatus({ message: '', type: '' });
  };

  return (
    <div className="container">
      <div className="card">
        
        <div className="tab-container">
          <button 
            className={`tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => switchTab('login')}
            disabled={isProcessing}
          >
            Login
          </button>
          <button 
            className={`tab ${activeTab === 'signup' ? 'active' : ''}`}
            onClick={() => switchTab('signup')}
            disabled={isProcessing}
          >
            Sign Up
          </button>
        </div>

        {!isReady ? (
          <div className="loading-state">
            <p>Loading WebAssembly Core...</p>
          </div>
        ) : (
          <div className="form-wrapper">
            {activeTab === 'login' ? (
              <Login onSubmit={handleAuth} isProcessing={isProcessing} />
            ) : (
              <SignUp onSubmit={handleAuth} isProcessing={isProcessing} />
            )}
          </div>
        )}

        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        )}

      </div>
    </div>
  );
}