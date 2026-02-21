import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, Upload, CheckCircle, AlertTriangle, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import type { Complaint } from '@/lib/api';

export default function OwnerComplaintsPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const data = await api.getOwnerComplaints(); // will add this method
      setComplaints(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleUploadProof = async (complaintId: string, file: File) => {
    const formData = new FormData();
    formData.append('proof', file);
    try {
      await api.uploadOwnerProof(complaintId, formData);
      // Refresh after successful upload
      fetchComplaints();
    } catch (err: any) {
      alert('Upload failed: ' + err.message);
    }
  };

  if (loading) return <AppLayout><div className="page-container">Loading...</div></AppLayout>;

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <div>
          <h1 className="page-title">Vehicle Complaints</h1>
          <p className="page-subtitle">Complaints filed against your vehicles</p>
        </div>

        {error && <div className="text-destructive bg-destructive/10 p-3 rounded-lg">{error}</div>}

        {complaints.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            No complaints found against your vehicles.
          </div>
        ) : (
          <div className="space-y-4">
            {complaints.map((complaint) => (
              <OwnerComplaintCard
                key={complaint.id}
                complaint={complaint}
                onUpload={(file) => handleUploadProof(complaint.id, file)}
              />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

function OwnerComplaintCard({ complaint, onUpload }: { complaint: Complaint; onUpload: (file: File) => void }) {
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    if (complaint.timer_end_time) {
      const end = new Date(complaint.timer_end_time).getTime();
      const updateTimer = () => {
        const now = Date.now();
        setTimeLeft(Math.max(0, Math.floor((end - now) / 1000)));
      };
      updateTimer();
      const interval = setInterval(updateTimer, 1000);
      return () => clearInterval(interval);
    }
  }, [complaint.timer_end_time]);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const isExpired = timeLeft === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-xl border border-border p-5 space-y-3"
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary">
              {complaint.vehicle_type.replace('_', ' ')}
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              complaint.status === 'resolved' ? 'bg-success/10 text-success' :
              complaint.status === 'fine_applied' ? 'bg-destructive/10 text-destructive' :
              complaint.status === 'timer_running' ? 'bg-warning/10 text-warning' :
              'bg-muted text-muted-foreground'
            }`}>
              {complaint.status.replace('_', ' ')}
            </span>
          </div>
          <h3 className="font-display font-semibold text-lg">
            {complaint.plate_number || 'Plate pending'}
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Reported: {new Date(complaint.recorded_at).toLocaleString()}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Location: {complaint.latitude.toFixed(4)}, {complaint.longitude.toFixed(4)}
          </p>
        </div>
        <div className="text-right">
          {complaint.fine_amount > 0 && (
            <p className="font-bold text-destructive">Fine: ₹{complaint.fine_amount}</p>
          )}
        </div>
      </div>

      {/* Timer for active complaints */}
      {complaint.status === 'timer_running' && timeLeft !== null && (
        <div className={`p-3 rounded-lg ${isExpired ? 'bg-destructive/10' : 'bg-warning/10'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className={`w-4 h-4 ${isExpired ? 'text-destructive' : 'text-warning'}`} />
              <span className="font-mono text-lg font-bold">
                {formatTime(timeLeft)}
              </span>
            </div>
            {isExpired ? (
              <span className="text-destructive text-sm font-semibold">Expired – Fine applied</span>
            ) : (
              <span className="text-warning text-sm">Remaining to respond</span>
            )}
          </div>
        </div>
      )}

      {/* Proof upload section */}
      {complaint.status === 'timer_running' && !isExpired && (
        <div className="border-t border-border pt-3 mt-2">
          <p className="text-sm font-medium mb-2">Upload proof of removal:</p>
          <div className="flex items-center gap-3">
            <input
              type="file"
              accept="image/*,video/*"
              id={`proof-${complaint.id}`}
              className="hidden"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => document.getElementById(`proof-${complaint.id}`)?.click()}
            >
              <FileText className="w-4 h-4 mr-1" /> Choose file
            </Button>
            {selectedFile && (
              <>
                <span className="text-xs text-muted-foreground truncate max-w-[150px]">
                  {selectedFile.name}
                </span>
                <Button
                  size="sm"
                  onClick={() => onUpload(selectedFile)}
                >
                  <Upload className="w-4 h-4 mr-1" /> Upload
                </Button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Resolved / Fine states */}
      {complaint.status === 'resolved' && (
        <div className="flex items-center gap-2 text-success border-t border-border pt-3">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm">Resolved – No fine</span>
        </div>
      )}
      {complaint.status === 'fine_applied' && (
        <div className="flex items-center gap-2 text-destructive border-t border-border pt-3">
          <AlertTriangle className="w-4 h-4" />
          <span className="text-sm">Fine applied – ₹{complaint.fine_amount}</span>
        </div>
      )}
    </motion.div>
  );
}