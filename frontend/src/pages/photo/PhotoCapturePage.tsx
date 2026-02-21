import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { useAppStore } from '@/store/useAppStore';
import { api } from '@/lib/api';

export default function PhotoCapturePage() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [cameraActive, setCameraActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play()
            .then(() => setCameraActive(true))
            .catch(err => setError('Could not start video playback.'));
        };
      } else {
        setError('Video element not found.');
      }
    } catch (err) {
      setError('Camera access denied. Please check permissions.');
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current && stream) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        setError('Video not ready. Please try again.');
        return;
      }
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg');
      setPhoto(dataUrl);
      
      // Stop camera
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setCameraActive(false);
    }
  };

  const retake = () => {
    setPhoto(null);
    startCamera();
  };

const confirmPhoto = async () => {
  if (!photo) return;
  setUploading(true);
  try {
    const blob = await fetch(photo).then(res => res.blob());
    const formData = new FormData();
    formData.append('image', blob, 'photo.jpg');
    const result = await api.uploadImage(formData);
    useAppStore.getState().setImageId(result.id);
    useAppStore.getState().setCapturedImage(result.image_url);
    navigate('/waiting-detection');
  } catch (err: any) {
    setError('Upload failed: ' + err.message);
  } finally {
    setUploading(false);
  }
};

  return (
    <AppLayout>
      <div className="page-container space-y-4">
        <h1 className="page-title">Take Vehicle Photo</h1>
        
        {error && (
          <div className="bg-destructive/10 text-destructive p-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Always render video, hide when not active */}
        <div className="relative bg-black rounded-lg overflow-hidden" style={{ minHeight: '300px', display: cameraActive ? 'block' : 'none' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            style={{ minHeight: '300px' }}
          />
        </div>

        {!cameraActive && !photo && (
          <Button onClick={startCamera} className="w-full">
            Open Camera
          </Button>
        )}

        {cameraActive && (
          <Button onClick={capturePhoto} className="w-full">
            Capture Photo
          </Button>
        )}

        {photo && (
          <div className="space-y-4">
            <img src={photo} alt="Captured" className="w-full rounded-lg border" />
            <div className="flex gap-2">
              <Button onClick={retake} variant="outline" className="flex-1">
                Retake
              </Button>
              <Button onClick={confirmPhoto} className="flex-1">
                Use Photo
              </Button>
            </div>
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </AppLayout>
  );
}
