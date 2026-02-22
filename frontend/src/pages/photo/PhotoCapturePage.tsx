import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Camera, Sun, MapPin, Car, CheckCircle, ArrowRight } from 'lucide-react';
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
  const [cameraActive, setCameraActive] = useState(false);
  const [showGuidelines, setShowGuidelines] = useState(true);
  const [videoReady, setVideoReady] = useState(false);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const startCamera = async () => {
    setError('');
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 2000 }
        }
      });
      setStream(mediaStream);
      setCameraActive(true);
      setShowGuidelines(false);
    } catch (err) {
      setError('Camera access denied. Please check permissions.');
    }
  };

  // Attach stream to video element when it becomes available
  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.onloadedmetadata = () => {
        videoRef.current?.play()
          .then(() => setVideoReady(true))
          .catch(() => setError('Could not start video playback.'));
      };
    }
  }, [stream]);

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current && stream) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d')?.drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      setPhoto(dataUrl);
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setCameraActive(false);
      setVideoReady(false);
    }
  };

  const retake = () => {
    setPhoto(null);
    startCamera();
  };

  const usePhoto = () => {
    if (photo) {
      useAppStore.getState().setCapturedImage(photo);
      navigate('/photo-confirm');
    }
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Take Vehicle Photo</h1>

        {error && (
          <div className="bg-destructive/10 text-destructive p-3 rounded-lg">
            {error}
          </div>
        )}

        {showGuidelines && !cameraActive && !photo && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Guidelines content (keep as before) */}
            <div className="space-y-3">
              <div className="flex items-start gap-4 p-4 bg-card rounded-xl border border-border">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Camera className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">1. Clear License Plate</h3>
                  <p className="text-sm text-muted-foreground">Ensure the number plate is clearly visible.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-card rounded-xl border border-border">
                <div className="w-10 h-10 rounded-full bg-warning/10 flex items-center justify-center shrink-0">
                  <Sun className="w-5 h-5 text-warning" />
                </div>
                <div>
                  <h3 className="font-semibold">2. Good Lighting</h3>
                  <p className="text-sm text-muted-foreground">Avoid shadows or glare.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-card rounded-xl border border-border">
                <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center shrink-0">
                  <MapPin className="w-5 h-5 text-success" />
                </div>
                <div>
                  <h3 className="font-semibold">3. Location Access</h3>
                  <p className="text-sm text-muted-foreground">GPS will be used to tag the location.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-card rounded-xl border border-border">
                <div className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center shrink-0">
                  <Car className="w-5 h-5 text-secondary" />
                </div>
                <div>
                  <h3 className="font-semibold">4. Vehicle Type</h3>
                  <p className="text-sm text-muted-foreground">You'll select it after taking the photo.</p>
                </div>
              </div>
            </div>

            <div className="bg-accent/30 p-4 rounded-xl flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-success shrink-0" />
              <p className="text-sm text-muted-foreground">
                Photos are uploaded securely. Plate detection will happen automatically or you can enter it manually.
              </p>
            </div>

            <Button onClick={startCamera} className="w-full h-12 text-base font-semibold">
              Start Camera <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </motion.div>
        )}

        {/* Camera view */}
        {cameraActive && !photo && (
          <div className="space-y-4">
            <div className="relative bg-black rounded-lg overflow-hidden w-full aspect-video max-h-[70vh]">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="absolute inset-0 w-full h-full object-cover"
              />
              {!videoReady && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                  <p className="text-white">Initializing camera...</p>
                </div>
              )}
            </div>
            <Button onClick={capturePhoto} className="w-full">
              Capture Photo
            </Button>
          </div>
        )}

        {/* Photo preview */}
        {photo && (
          <div className="space-y-4">
            <img src={photo} alt="Captured" className="w-full rounded-lg border" />
            <div className="flex gap-2">
              <Button onClick={retake} variant="outline" className="flex-1">
                Retake
              </Button>
              <Button onClick={usePhoto} className="flex-1">
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