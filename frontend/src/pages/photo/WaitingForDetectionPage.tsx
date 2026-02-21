import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { useAppStore } from '@/store/useAppStore';

export default function WaitingForDetectionPage() {
  const navigate = useNavigate();
  const { imageId, setDetectedPlate } = useAppStore();
  const [error, setError] = useState('');

  useEffect(() => {
    if (!imageId) {
      navigate('/photo-capture');
      return;
    }
    const interval = setInterval(async () => {
      try {
        const result = await api.getDetection(imageId);
        if (result.status === 'completed' && result.plate) {
          setDetectedPlate(result.plate);
          navigate('/photo-confirm');
        } else if (result.status === 'error') {
          setError('Detection failed');
          clearInterval(interval);
        }
      } catch (err) {
        // ignore
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [imageId, navigate, setDetectedPlate]);

  const handleManual = () => {
    navigate('/manual-plate');
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6 text-center">
        <h1 className="page-title">Processing Image</h1>
        <p className="text-muted-foreground">Waiting for plate detection...</p>
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        {error && <p className="text-destructive">{error}</p>}
        <Button onClick={handleManual} variant="outline" className="mt-4">
          Enter Plate Manually
        </Button>
      </div>
    </AppLayout>
  );
}