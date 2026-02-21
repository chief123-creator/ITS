import { useNavigate } from 'react-router-dom';
import { Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { useAppStore } from '@/store/useAppStore';

export default function PhotoConfirmPage() {
  const navigate = useNavigate();
  const { detectedPlate, capturedImage } = useAppStore();

  const handleYes = () => {
    navigate('/action-select'); // Go to action selection with plate stored
  };

  const handleNo = () => {
    // Clear and retake
    useAppStore.getState().setDetectedPlate(null);
    useAppStore.getState().setCapturedImage(null);
    navigate('/photo-capture');
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Confirm Vehicle Number</h1>
        {capturedImage && (
          <img src={capturedImage} alt="Vehicle" className="w-full rounded-lg" />
        )}
        <div className="bg-card p-6 rounded-xl text-center">
          <p className="text-sm text-muted-foreground">Detected Plate</p>
          <p className="text-3xl font-mono font-bold my-4">{detectedPlate || 'Not detected'}</p>
          <p className="text-sm mb-6">Is this correct?</p>
          <div className="flex gap-4">
            <Button onClick={handleYes} className="flex-1" variant="default">
              <Check className="mr-2" /> Yes
            </Button>
            <Button onClick={handleNo} className="flex-1" variant="destructive">
              <X className="mr-2" /> No
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}