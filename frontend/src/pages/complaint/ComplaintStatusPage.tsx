import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle2, Clock, Bell, AlertTriangle, FileText, MessageCircle } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const steps = [
  { key: 'pending', label: 'Report Submitted', icon: FileText },
  { key: 'timer_running', label: 'Owner Notified', icon: Bell },
  { key: 'resolved', label: 'Awaiting Resolution', icon: Clock },
  { key: 'fine_applied', label: 'Final Decision', icon: AlertTriangle },
];

const statusOrder = ['pending', 'timer_running', 'resolved', 'fine_applied'];

const ComplaintStatusPage = () => {
  const navigate = useNavigate();
  const { currentComplaint } = useAppStore();
  const [timeLeft, setTimeLeft] = useState('');

  // Use mock if no real complaint
  const complaint = currentComplaint || {
    id: 'demo-001',
    status: 'timer_running' as const,
    timer_end_time: new Date(Date.now() + 1800000).toISOString(),
    vehicle_type: 'four_wheeler' as const,
    action_type: 'direct_call' as const,
    fine_amount: 500,
    created_at: new Date().toISOString(),
  };

  const currentStepIndex = statusOrder.indexOf(complaint.status);

  useEffect(() => {
    if (!complaint.timer_end_time) return;
    const update = () => {
      const diff = new Date(complaint.timer_end_time!).getTime() - Date.now();
      if (diff <= 0) { setTimeLeft('00:00'); return; }
      const m = Math.floor(diff / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      setTimeLeft(`${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`);
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [complaint.timer_end_time]);

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-2">Complaint Status</h1>
        <p className="text-muted-foreground mb-8">Track the progress of your report</p>

        {/* Timer */}
        {complaint.status === 'timer_running' && timeLeft && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="gradient-warning rounded-2xl p-6 mb-8 text-center">
            <p className="text-sm text-warning-foreground/80 mb-2">Time remaining for owner to move vehicle</p>
            <p className="text-5xl font-bold font-mono text-warning-foreground">{timeLeft}</p>
          </motion.div>
        )}

        {/* Status resolved */}
        {(complaint.status === 'resolved' || complaint.status === 'fine_applied') && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className={`rounded-2xl p-6 mb-8 text-center ${complaint.status === 'resolved' ? 'gradient-success' : 'gradient-destructive'}`}>
            <CheckCircle2 className="h-10 w-10 mx-auto mb-2 text-primary-foreground" />
            <p className="text-lg font-semibold text-primary-foreground">
              {complaint.status === 'resolved' ? 'Vehicle Moved! Issue Resolved.' : `Fine of ₹${complaint.fine_amount} Applied`}
            </p>
          </motion.div>
        )}

        {/* Progress Timeline */}
        <div className="space-y-0 mb-8">
          {steps.map((step, i) => {
            const isComplete = i <= currentStepIndex;
            const isCurrent = i === currentStepIndex;
            return (
              <div key={step.key} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center shrink-0 ${
                    isComplete ? 'gradient-primary' : 'bg-muted'
                  } ${isCurrent ? 'ring-4 ring-primary/20' : ''}`}>
                    <step.icon className={`h-4 w-4 ${isComplete ? 'text-primary-foreground' : 'text-muted-foreground'}`} />
                  </div>
                  {i < steps.length - 1 && (
                    <div className={`w-0.5 h-12 ${i < currentStepIndex ? 'gradient-primary' : 'bg-muted'}`} />
                  )}
                </div>
                <div className="pb-8">
                  <p className={`font-medium ${isComplete ? 'text-foreground' : 'text-muted-foreground'}`}>{step.label}</p>
                  {isCurrent && <p className="text-sm text-primary">In Progress</p>}
                </div>
              </div>
            );
          })}
        </div>

        {/* Details */}
        <div className="bg-card rounded-2xl border border-border p-6 mb-6">
          <h3 className="font-semibold text-foreground mb-3">Report Details</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">ID</span><span className="font-mono text-foreground">{complaint.id}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Vehicle</span><span className="text-foreground capitalize">{complaint.vehicle_type.replace('_', ' ')}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Action</span><span className="text-foreground capitalize">{complaint.action_type.replace('_', ' ')}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Filed</span><span className="text-foreground">{new Date(complaint.created_at).toLocaleString()}</span></div>
          </div>
        </div>

        <div className="flex gap-3">
          <button onClick={() => navigate('/dashboard')}
            className="flex-1 py-3 rounded-xl border border-border text-foreground font-medium hover:bg-muted transition-colors">
            Dashboard
          </button>
          <button className="flex-1 py-3 rounded-xl gradient-primary text-primary-foreground font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
            <MessageCircle className="h-4 w-4" /> Contact Support
          </button>
        </div>
      </div>
    </AppLayout>
  );
};

export default ComplaintStatusPage;
