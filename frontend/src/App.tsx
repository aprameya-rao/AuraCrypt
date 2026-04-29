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

  const convertMedia = async (file: File, outputName: string, outputMime: string): Promise<File> => {
    const ffmpeg = ffmpegRef.current;
    const inputName = `input_${file.name.replace(/\s+/g, '_')}`; // Sanitize spaces
    
    await ffmpeg.writeFile(inputName, await fetchFile(file));
    await ffmpeg.exec(['-i', inputName, outputName]);
    const data = await ffmpeg.readFile(outputName);
    
    const blob = new Blob([data], { type: outputMime });
    return new File([blob], outputName, { type: outputMime });
  };

  const handleAuth = async (username: string, pass: string, video: File, audio: File, isLogin: boolean) => {
    setIsProcessing(true);
    setStatus({ message: "Transcoding media locally...", type: "info" });

    try {
      // 1. Convert media using FFmpeg
      const finalVideo = await convertMedia(video, 'video.mp4', 'video/mp4');
      const finalAudio = await convertMedia(audio, 'audio.wav', 'audio/wav');

      setStatus({ message: "Connecting to server...", type: "info" });

      // 2. Package everything into FormData
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', pass);
      formData.append('video_file', finalVideo);
      formData.append('audio_file', finalAudio);

      // 3. Call the backend via our api.ts functions
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
    if (isProcessing) return; // Prevent switching while processing
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