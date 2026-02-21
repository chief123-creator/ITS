import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Clock, ArrowRight, ArrowLeft } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';
import type { VehicleType } from '@/types';

const vehicleOptions: { value: VehicleType; label: string; emoji: string }[] = [
  { value: 'two_wheeler', label: 'Two Wheeler', emoji: '🏍️' },
  { value: 'four_wheeler', label: 'Four Wheeler', emoji: '🚗' },
  { value: 'truck', label: 'Truck / Heavy', emoji: '🚛' },
];

const VideoPreviewPage = () => {
  const navigate = useNavigate();
  const { currentVideo, setCurrentVideo } = useAppStore();
  const [vehicleType, setVehicleType] = useState<VehicleType>('four_wheeler');

  const videoUrl = useMemo(() => {
    return currentVideo?.videoBlob ? URL.createObjectURL(currentVideo.videoBlob) : null;
  }, [currentVideo?.videoBlob]);

  if (!currentVideo) {
    navigate('/camera');
    return null;
  }

  const handleContinue = () => {
    setCurrentVideo({ ...currentVideo, vehicleType });
    navigate('/action-select');
  };

  const formatDuration = (s: number) => `${Math.floor(s / 60)}m ${s % 60}s`;

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-2">Review Recording</h1>
        <p className="text-muted-foreground mb-6">Verify your evidence before submitting</p>

        {videoUrl && (
          <div className="rounded-2xl overflow-hidden bg-foreground/5 mb-6">
            <video src={videoUrl} controls className="w-full aspect-video object-cover" />
          </div>
        )}

        <div className="flex gap-4 mb-6">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-border text-sm">
            <MapPin className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">{currentVideo.latitude.toFixed(4)}, {currentVideo.longitude.toFixed(4)}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-border text-sm">
            <Clock className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">{formatDuration(currentVideo.duration)}</span>
          </div>
        </div>

        <div className="mb-6">
          <label className="text-sm font-medium text-foreground mb-3 block">Vehicle Type</label>
          <div className="grid grid-cols-3 gap-3">
            {vehicleOptions.map((opt) => (
              <button key={opt.value} onClick={() => setVehicleType(opt.value)}
                className={`p-4 rounded-xl border-2 text-center transition-all ${
                  vehicleType === opt.value
                    ? 'border-primary bg-primary/5'
                    : 'border-border bg-card hover:border-primary/30'
                }`}>
                <span className="text-2xl block mb-1">{opt.emoji}</span>
                <span className="text-xs font-medium text-foreground">{opt.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button onClick={() => navigate('/camera/record')}
            className="flex-1 py-3 rounded-xl border border-border text-foreground font-medium flex items-center justify-center gap-2 hover:bg-muted transition-colors">
            <ArrowLeft className="h-4 w-4" /> Re-record
          </button>
          <button onClick={handleContinue}
            className="flex-1 py-3 rounded-xl gradient-primary text-primary-foreground font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
            Continue <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </AppLayout>
  );
};

export default VideoPreviewPage;
