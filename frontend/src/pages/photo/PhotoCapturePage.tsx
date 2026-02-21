import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { useAppStore } from '@/store/useAppStore';

export default function PhotoCapturePage() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [error, setError] = useState('');

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      if (videoRef.current) videoRef.current.srcObject = mediaStream;
    } catch {
      setError('Camera access denied');
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;
      const ctx = canvasRef.current.getContext('2d');
      ctx?.drawImage(videoRef.current, 0, 0);
      const dataUrl = canvasRef.current.toDataURL('image/jpeg');
      setPhoto(dataUrl);
      stream?.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const retake = () => {
    setPhoto(null);
    startCamera();
  };

  const confirmPhoto = async () => {
    if (!photo) return;
    // Convert data URL to blob and upload (mock detection for now)
    const blob = await fetch(photo).then(res => res.blob());
    const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
    
    // Mock detected plate – replace with API call later
    useAppStore.getState().setDetectedPlate('MH12AB1234');
    useAppStore.getState().setCapturedImage(photo);
    navigate('/photo-confirm');
  };

  return (
    <AppLayout>
      <div className="page-container space-y-4">
        <h1 className="page-title">Take Vehicle Photo</h1>
        {error && <p className="text-destructive">{error}</p>}
        {!stream && !photo && (
          <Button onClick={startCamera} className="w-full">Open Camera</Button>
        )}
        {stream && (
          <>
            <video ref={videoRef} autoPlay className="w-full rounded-lg" />
            <Button onClick={capturePhoto} className="w-full">Capture</Button>
          </>
        )}
        {photo && (
          <>
            <img src={photo} alt="Captured" className="w-full rounded-lg" />
            <div className="flex gap-2">
              <Button onClick={retake} variant="outline" className="flex-1">Retake</Button>
              <Button onClick={confirmPhoto} className="flex-1">Use Photo</Button>
            </div>
          </>
        )}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </AppLayout>
  );
}