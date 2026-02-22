import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { useAppStore } from '@/store/useAppStore';

export default function PhotoConfirmPage() {
  const navigate = useNavigate();
  const { detectedPlate, capturedImage } = useAppStore();

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Confirm Plate</h1>
        {capturedImage && (
          <img src={capturedImage} alt="Vehicle" className="w-full rounded-lg border" />
        )}
        <p className="text-center text-2xl font-mono font-bold">{detectedPlate}</p>
        <div className="flex gap-4">
          <Button onClick={() => navigate('/photo-capture')} variant="outline" className="flex-1">
            Retake
          </Button>
          <Button onClick={() => navigate('/action-select')} className="flex-1">
            Confirm
          </Button>
        </div>
      </div>
    </AppLayout>
  );
}