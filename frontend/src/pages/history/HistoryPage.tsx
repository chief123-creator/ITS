import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Car, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import type { Complaint } from '@/lib/api';

export default function HistoryPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getComplaints()
      .then(setComplaints)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  if (loading) return <AppLayout><div className="page-container">Loading...</div></AppLayout>;

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Complaint History</h1>
        {error && <div className="text-destructive bg-destructive/10 p-3 rounded">{error}</div>}
        {complaints.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">No complaints yet.</p>
        ) : (
          <div className="space-y-4">
            {complaints.map((c) => (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-card p-4 rounded-xl border border-border space-y-2"
              >
                <div className="flex justify-between items-start">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    c.status === 'resolved' ? 'bg-success/10 text-success' :
                    c.status === 'fine_applied' ? 'bg-destructive/10 text-destructive' :
                    c.status === 'timer_running' ? 'bg-warning/10 text-warning' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {c.status.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-muted-foreground">{formatDate(c.created_at)}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Car className="w-4 h-4" /> {c.vehicle_type.replace('_', ' ')}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="w-4 h-4" /> {c.latitude.toFixed(4)}, {c.longitude.toFixed(4)}
                </div>
                {c.plate_number && (
                  <div className="text-sm font-mono">Plate: {c.plate_number}</div>
                )}
                {c.video_url && (
                  <video src={`http://localhost:8000${c.video_url}`} controls className="w-full rounded-lg mt-2 max-h-40" />
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}