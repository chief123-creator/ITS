import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { useAppStore } from '@/store/useAppStore';

export default function PhotoCapturePage() {
  const navigate = useNavigate();
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      alert('Camera access denied');
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && stream) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
          setFile(file);
          setImage(URL.createObjectURL(blob));
        }
      }, 'image/jpeg');
      // Stop camera
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('image', file);
    try {
      const result = await api.detectPlate(formData);
      // Store plate and image in store (extend store)
      useAppStore.getState().setDetectedPlate(result.plate);
      useAppStore.getState().setCapturedImage(image);
      navigate('/photo-confirm');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="page-container">
        <h1 className="page-title">Take Vehicle Photo</h1>
        {!stream && !image && (
          <div className="space-y-4">
            <Button onClick={startCamera} className="w-full">
              <Camera className="mr-2" /> Open Camera
            </Button>
            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
              <Upload className="mr-2" /> Upload Photo
            </Button>
            <input
              type="file"
              accept="image/*"
              ref={fileInputRef}
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setFile(f);
                  setImage(URL.createObjectURL(f));
                }
              }}
            />
          </div>
        )}
        {stream && (
          <div>
            <video ref={videoRef} autoPlay className="w-full rounded-lg" />
            <Button onClick={capturePhoto} className="mt-4 w-full">Capture</Button>
          </div>
        )}
        {image && (
          <div>
            <img src={image} alt="Captured" className="w-full rounded-lg" />
            <Button onClick={handleUpload} disabled={loading} className="mt-4 w-full">
              {loading ? 'Detecting...' : 'Detect Plate'}
            </Button>
          </div>
        )}
      </div>
    </AppLayout>
  );
}