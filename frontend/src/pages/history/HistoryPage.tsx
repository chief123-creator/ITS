import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Clock } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const statusConfig: Record<string, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-warning/10 text-warning' },
  timer_running: { label: 'Timer', className: 'bg-primary/10 text-primary' },
  resolved: { label: 'Resolved', className: 'bg-success/10 text-success' },
  fine_applied: { label: 'Fined', className: 'bg-destructive/10 text-destructive' },
};

const filters: { value: string; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'timer_running', label: 'Active' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'fine_applied', label: 'Fined' },
];

const HistoryPage = () => {
  const { complaints, getComplaints } = useAppStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    getComplaints();
  }, [getComplaints]);

  const filtered = complaints.filter((c) => {
    if (filter !== 'all' && c.status !== filter) return false;
    if (search && !c.id.toLowerCase().includes(search.toLowerCase()) && !c.vehicle_type.includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-6">Report History</h1>

        {/* Search & Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search reports..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm" />
          </div>
          <div className="flex gap-2">
            {filters.map((f) => (
              <button key={f.value} onClick={() => setFilter(f.value)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  filter === f.value ? 'gradient-primary text-primary-foreground' : 'bg-card border border-border text-muted-foreground hover:text-foreground'
                }`}>
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* List */}
        <motion.div initial="hidden" animate="show"
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
          className="space-y-3">
          {filtered.map((c) => (
            <motion.div key={c.id}
              variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}
              className="flex items-center justify-between p-4 rounded-xl bg-card border border-border hover:shadow-md transition-all cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-muted flex items-center justify-center">
                  <Clock className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium text-foreground">{c.id}</p>
                  <p className="text-sm text-muted-foreground capitalize">{c.vehicle_type.replace('_', ' ')} · {c.action_type.replace('_', ' ')}</p>
                </div>
              </div>
              <div className="text-right">
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig[c.status]?.className}`}>
                  {statusConfig[c.status]?.label}
                </span>
                <p className="text-xs text-muted-foreground mt-1">{new Date(c.created_at).toLocaleDateString()}</p>
              </div>
            </motion.div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">No reports found</div>
          )}
        </motion.div>
      </div>
    </AppLayout>
  );
};

export default HistoryPage;
