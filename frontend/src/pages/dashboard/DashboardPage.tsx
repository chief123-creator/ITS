import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FileText, AlertTriangle, Trophy, TrendingUp, Shield, Camera, History, ArrowRight, Clock, MoreVertical
} from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const statusConfig: Record<string, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-warning/10 text-warning' },
  timer_running: { label: 'Timer Running', className: 'bg-primary/10 text-primary' },
  resolved: { label: 'Resolved', className: 'bg-success/10 text-success' },
  fine_applied: { label: 'Fine Applied', className: 'bg-destructive/10 text-destructive' },
};

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, dashboardStats, complaints, isLoading, getDashboardStats, getComplaints } = useAppStore();

  // useEffect(() => {
  //   getDashboardStats();
  //   getComplaints();
  // }, [getDashboardStats, getComplaints]);

  const statCards = [
    { label: 'Total Reports', value: dashboardStats?.totalReports || 0, icon: FileText, gradient: 'gradient-primary' },
    { label: 'Active Issues', value: dashboardStats?.activeIssues || 0, icon: AlertTriangle, gradient: 'gradient-warning' },
    { label: 'Reward Points', value: dashboardStats?.rewards || 0, icon: Trophy, gradient: 'gradient-success' },
    { label: 'Success Rate', value: `${dashboardStats?.successRate || 0}%`, icon: TrendingUp, gradient: 'gradient-primary' },
  ];

  const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
  const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">
            Welcome back, {user?.name?.split(' ')[0] || 'User'} 👋
          </h1>
          <p className="text-muted-foreground mt-1">Here's your enforcement activity overview</p>
        </div>

        {/* Trust Score Banner */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="gradient-dark rounded-2xl p-6 mb-8 flex items-center justify-between">
          <div>
            <p className="text-primary-foreground/70 text-sm">Trust Score</p>
            <p className="text-3xl font-bold text-primary-foreground">{dashboardStats?.trustScore || 0}/100</p>
          </div>
          <div className="relative">
            <div className="h-16 w-16 rounded-full border-4 border-primary-foreground/20 flex items-center justify-center">
              <Shield className="h-7 w-7 text-primary-foreground" />
            </div>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary animate-spin" style={{ animationDuration: '3s' }} />
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((stat) => (
            <motion.div key={stat.label} variants={item} className={`stat-card ${stat.gradient} rounded-2xl`}>
              <stat.icon className="h-5 w-5 mb-3 opacity-80" />
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm opacity-80">{stat.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <div role="button" onClick={() => navigate('/camera')}
            className="flex items-center gap-4 p-5 rounded-2xl bg-card border border-border hover:border-primary/30 hover:shadow-lg transition-all text-left group cursor-pointer">
            <div className="h-12 w-12 rounded-xl gradient-primary flex items-center justify-center shrink-0">
              <Camera className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-foreground">New Report</p>
              <p className="text-sm text-muted-foreground">Record & submit a violation</p>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={(e) => { e.stopPropagation(); navigate('/camera/record?autoStart=1'); }}
                className="p-2 rounded-md hover:bg-muted/50 text-muted-foreground">
                <MoreVertical className="h-4 w-4" />
              </button>
              <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
          </div>
          <button onClick={() => navigate('/history')}
            className="flex items-center gap-4 p-5 rounded-2xl bg-card border border-border hover:border-primary/30 hover:shadow-lg transition-all text-left group">
            <div className="h-12 w-12 rounded-xl bg-secondary flex items-center justify-center shrink-0">
              <History className="h-5 w-5 text-foreground" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-foreground">View History</p>
              <p className="text-sm text-muted-foreground">Track your submissions</p>
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
          </button>
        </div>

        {/* Recent Reports */}
        <div className="bg-card rounded-2xl border border-border p-6">
          <h2 className="font-semibold text-foreground mb-4">Recent Reports</h2>
          <div className="space-y-3">
            {complaints.slice(0, 5).map((c) => (
              <div key={c.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground capitalize">{c.vehicle_type.replace('_', ' ')}</p>
                    <p className="text-xs text-muted-foreground">{new Date(c.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig[c.status]?.className || ''}`}>
                  {statusConfig[c.status]?.label || c.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default DashboardPage;
