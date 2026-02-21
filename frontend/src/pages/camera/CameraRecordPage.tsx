import { useRef, useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Circle, Square, Clock, MapPin, AlertCircle } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const CameraRecordPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setCurrentVideo } = useAppStore();
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [recording, setRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [error, setError] = useState('');
  const timerRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    const init = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: true,
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch {
        setError('Camera access denied. Please allow camera permissions.');
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => setCoords({ lat: 0, lng: 0 })
      );
    };
    init();
    return () => { stream?.getTracks().forEach((t) => t.stop()); };
  }, []);

  const startRecording = useCallback(() => {
    if (!stream) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      setCurrentVideo({
        videoBlob: blob,
        latitude: coords?.lat || 0,
        longitude: coords?.lng || 0,
        duration,
      });
      stream.getTracks().forEach((t) => t.stop());
      navigate('/camera/preview');
    };
    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);
    setDuration(0);
    timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
  }, [stream, coords, navigate, setCurrentVideo, duration]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
    if (timerRef.current) clearInterval(timerRef.current);
  }, []);

  const autoStart = new URLSearchParams(location.search).get('autoStart') === '1' || new URLSearchParams(location.search).get('autoStart') === 'true';

  useEffect(() => {
    if (stream && autoStart && !recording) {
      startRecording();
    }
  }, [stream, autoStart, recording, startRecording]);

  const formatTime = (s: number) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;

  if (error) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <AlertCircle className="h-12 w-12 text-destructive mb-4" />
          <h2 className="text-lg font-semibold text-foreground mb-2">Camera Access Required</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button onClick={() => window.location.reload()}
            className="px-4 py-2 rounded-lg gradient-primary text-primary-foreground text-sm font-medium">
            Retry
          </button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <div className="relative rounded-2xl overflow-hidden bg-foreground/5 aspect-video mb-6">
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />

          {/* Recording indicator */}
          {recording && (
            <div className="absolute top-4 left-4 flex items-center gap-2 bg-destructive/90 text-destructive-foreground px-3 py-1.5 rounded-full text-sm font-medium">
              <div className="h-2 w-2 rounded-full bg-destructive-foreground animate-pulse" />
              REC
            </div>
          )}

          {/* Timer */}
          <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-foreground/70 text-background px-3 py-1.5 rounded-full text-sm font-mono">
            <Clock className="h-3 w-3" /> {formatTime(duration)}
          </div>

          {/* Location */}
          {coords && (
            <div className="absolute bottom-4 left-4 flex items-center gap-1.5 bg-foreground/70 text-background px-3 py-1.5 rounded-full text-xs">
              <MapPin className="h-3 w-3" /> {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}
            </div>
          )}
        </div>

        <div className="flex justify-center">
          {!recording ? (
            <motion.button whileTap={{ scale: 0.9 }} onClick={startRecording}
              className="h-16 w-16 rounded-full gradient-destructive flex items-center justify-center shadow-xl hover:opacity-90 transition-opacity">
              <Circle className="h-7 w-7 text-destructive-foreground fill-current" />
            </motion.button>
          ) : (
            <motion.button whileTap={{ scale: 0.9 }} onClick={stopRecording}
              className="h-16 w-16 rounded-full bg-destructive flex items-center justify-center shadow-xl hover:opacity-90 transition-opacity">
              <Square className="h-6 w-6 text-destructive-foreground fill-current" />
            </motion.button>
          )}
        </div>
        <p className="text-center text-sm text-muted-foreground mt-4">
          {recording ? 'Tap to stop recording' : 'Tap to start recording'}
        </p>
      </div>
    </AppLayout>
  );
};

export default CameraRecordPage;
