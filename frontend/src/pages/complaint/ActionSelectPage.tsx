import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, FileText, Loader2 } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

export default function ActionSelectPage() {
  const navigate = useNavigate();
  const { currentVideo, detectedPlate, submitComplaint } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleDirectCall = () => {
    if (!detectedPlate) {
      setError('No plate detected');
      return;
    }
    navigate(`/owner/by-plate/${detectedPlate}`);
  };

  const handleOfficialIssue = async () => {
    if (!detectedPlate) {
      setError('No plate detected. Please capture a photo first.');
      return;
    }

    // If no video yet, go to camera record
    if (!currentVideo) {
      navigate('/camera/record');
      return;
    }

    // Otherwise, submit complaint
    setLoading(true);
    const formData = new FormData();
    const videoFile = new File([currentVideo.videoBlob], 'recording.mp4', { type: 'video/mp4' });
    formData.append('video', videoFile);
    formData.append('vehicle_type', currentVideo.vehicleType || 'four_wheeler');
    formData.append('action_type', 'official_issue');
    formData.append('latitude', currentVideo.latitude.toString());
    formData.append('longitude', currentVideo.longitude.toString());
    formData.append('recorded_at', new Date().toISOString());
    formData.append('plate_number', detectedPlate);

    try {
      const complaint = await submitComplaint(formData);
      navigate('/complaint/status');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Choose Action</h1>
        {error && <div className="text-destructive bg-destructive/10 p-3 rounded">{error}</div>}
        <div className="space-y-4">
          <motion.button
            onClick={handleDirectCall}
            disabled={loading}
            className="w-full p-6 bg-card border-2 border-success/25 rounded-2xl text-left"
          >
            <Phone className="w-6 h-6 text-success mb-2" />
            <h3 className="font-bold text-lg">Direct Call</h3>
            <p className="text-sm text-muted-foreground">Contact owner immediately</p>
          </motion.button>
          <motion.button
            onClick={handleOfficialIssue}
            disabled={loading}
            className="w-full p-6 bg-card border border-border rounded-2xl text-left"
          >
            <FileText className="w-6 h-6 text-primary mb-2" />
            <h3 className="font-bold text-lg">Official Issue</h3>
            <p className="text-sm text-muted-foreground">Start 24h timer, owner must respond</p>
          </motion.button>
        </div>
        {loading && <Loader2 className="animate-spin mx-auto" />}
      </div>
    </AppLayout>
  );
}