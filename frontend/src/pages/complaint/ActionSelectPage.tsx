import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, FileText, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';
import type { ActionType } from '@/types';

const actions: { type: ActionType; title: string; desc: string; icon: typeof Phone; recommended?: boolean }[] = [
  { type: 'direct_call', title: 'Direct Call', desc: 'Owner is contacted immediately. Faster resolution with timer countdown.', icon: Phone, recommended: true },
  { type: 'official_issue', title: 'Official Issue', desc: 'Filed as an official complaint. Processed through authorities.', icon: FileText },
];

const ActionSelectPage = () => {
  const navigate = useNavigate();
  const { currentVideo, submitComplaint, isLoading, clearCurrentVideo } = useAppStore();
  const [localError, setLocalError] = useState('');

  if (!currentVideo?.videoBlob) {
    navigate('/camera');
    return null;
  }

  const handleSelect = async (actionType: ActionType) => {
    setLocalError('');

    const videoFile = new File([currentVideo.videoBlob], 'recording.mp4', { type: 'video/mp4' });
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('vehicle_type', currentVideo.vehicleType || 'four_wheeler');
    formData.append('action_type', actionType);
    formData.append('latitude', currentVideo.latitude.toString());
    formData.append('longitude', currentVideo.longitude.toString());
    formData.append('recorded_at', new Date().toISOString());

    try {
      await submitComplaint(formData);
      clearCurrentVideo();
      navigate('/complaint/status');
    } catch (err: any) {
      setLocalError(err.message);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-2">Choose Action</h1>
        <p className="text-muted-foreground mb-8">How should this violation be handled?</p>

        {localError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6 p-4 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2"
          >
            <AlertCircle className="h-4 w-4 shrink-0" /> {localError}
          </motion.div>
        )}

        <div className="space-y-4">
          {actions.map((action) => (
            <motion.button
              key={action.type}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => handleSelect(action.type)}
              disabled={isLoading}
              className={`w-full p-6 rounded-2xl border-2 text-left transition-all flex items-start gap-4 ${
                action.recommended ? 'border-primary bg-primary/5' : 'border-border bg-card hover:border-primary/30'
              } disabled:opacity-50`}>
              <div className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${
                action.recommended ? 'gradient-primary' : 'bg-muted'
              }`}>
                <action.icon className={`h-5 w-5 ${action.recommended ? 'text-primary-foreground' : 'text-foreground'}`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-semibold text-foreground">{action.title}</p>
                  {action.recommended && (
                    <span className="px-2 py-0.5 rounded-full gradient-success text-xs font-medium text-success-foreground">
                      Recommended
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">{action.desc}</p>
              </div>
              {isLoading ? <Loader2 className="h-5 w-5 animate-spin text-muted-foreground mt-1" /> : <ArrowRight className="h-5 w-5 text-muted-foreground mt-1" />}
            </motion.button>
          ))}
        </div>
      </div>
    </AppLayout>
  );
};

export default ActionSelectPage;
