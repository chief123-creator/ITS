import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import AppLayout from '@/components/AppLayout';
import { useAppStore } from '@/store/useAppStore';

export default function ManualPlatePage() {
  const navigate = useNavigate();
  const { capturedImage, setDetectedPlate } = useAppStore();
  const [plate, setPlate] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    if (!plate.trim()) {
      setError('Please enter a plate number');
      return;
    }
    setDetectedPlate(plate.toUpperCase());
    navigate('/photo-confirm');
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Enter Plate Manually</h1>
        {capturedImage && (
          <img src={capturedImage} alt="Vehicle" className="w-full rounded-lg border" />
        )}
        <div className="space-y-4">
          <Input
            placeholder="Enter plate number (e.g., MH12AB1234)"
            value={plate}
            onChange={(e) => setPlate(e.target.value)}
            className="uppercase"
          />
          {error && <p className="text-destructive text-sm">{error}</p>}
          <Button onClick={handleSubmit} className="w-full">
            Continue
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}