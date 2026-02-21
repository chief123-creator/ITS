import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Mail, Phone, Shield, CreditCard, LogOut, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const aadhaarStatusConfig: Record<string, { label: string; className: string }> = {
  verified: { label: 'Verified', className: 'bg-success/10 text-success' },
  unverified: { label: 'Unverified', className: 'bg-warning/10 text-warning' },
  pending: { label: 'Pending', className: 'bg-primary/10 text-primary' },
  rejected: { label: 'Rejected', className: 'bg-destructive/10 text-destructive' },
};

const accountStatusConfig: Record<string, { label: string; className: string }> = {
  active: { label: 'Active', className: 'bg-success/10 text-success' },
  warned: { label: 'Warned', className: 'bg-warning/10 text-warning' },
  suspended: { label: 'Suspended', className: 'bg-destructive/10 text-destructive' },
  banned: { label: 'Banned', className: 'bg-destructive/10 text-destructive' },
};

const SettingsPage = () => {
  const navigate = useNavigate();
  const { user, updateUser, logout, isLoading } = useAppStore();
  const [form, setForm] = useState({ name: user?.name || '', email: user?.email || '', phone: user?.phone || '' });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateUser(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-6">Settings</h1>

        {/* Profile Card */}
        <div className="bg-card rounded-2xl border border-border p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="h-16 w-16 rounded-2xl gradient-primary flex items-center justify-center text-2xl font-bold text-primary-foreground">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">{user?.name || 'User'}</h2>
              <p className="text-sm text-muted-foreground">{user?.email || ''}</p>
              <div className="flex gap-2 mt-2">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${aadhaarStatusConfig[user?.aadhaar_status || 'unverified']?.className}`}>
                  <CreditCard className="h-3 w-3 inline mr-1" />
                  {aadhaarStatusConfig[user?.aadhaar_status || 'unverified']?.label}
                </span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${accountStatusConfig[user?.account_status || 'active']?.className}`}>
                  <Shield className="h-3 w-3 inline mr-1" />
                  {accountStatusConfig[user?.account_status || 'active']?.label}
                </span>
              </div>
            </div>
          </div>

          {/* Trust Points */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-muted/50 mb-4">
            <span className="text-sm text-muted-foreground">Trust Points</span>
            <span className="font-bold text-foreground">{user?.trust_points || 0}</span>
          </div>
        </div>

        {/* Edit Profile */}
        <div className="bg-card rounded-2xl border border-border p-6 mb-6">
          <h3 className="font-semibold text-foreground mb-4">Edit Profile</h3>
          {saved && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="mb-4 p-3 rounded-lg bg-success/10 border border-success/20 text-success text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" /> Profile updated successfully!
            </motion.div>
          )}
          <form onSubmit={handleSave} className="space-y-4">
            {[
              { key: 'name', label: 'Name', icon: User, type: 'text' },
              { key: 'email', label: 'Email', icon: Mail, type: 'email' },
              { key: 'phone', label: 'Phone', icon: Phone, type: 'tel' },
            ].map(({ key, label, icon: Icon, type }) => (
              <div key={key}>
                <label className="text-sm font-medium text-foreground mb-1.5 block">{label}</label>
                <div className="relative">
                  <Icon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input type={type} value={form[key as keyof typeof form]}
                    onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm" />
                </div>
              </div>
            ))}
            <button type="submit" disabled={saving}
              className="px-6 py-2.5 rounded-lg gradient-primary text-primary-foreground font-medium text-sm flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Danger Zone */}
        <div className="bg-card rounded-2xl border border-destructive/20 p-6">
          <h3 className="font-semibold text-foreground mb-2">Account</h3>
          <p className="text-sm text-muted-foreground mb-4">Sign out of your account</p>
          <button onClick={handleLogout}
            className="px-6 py-2.5 rounded-lg bg-destructive/10 text-destructive font-medium text-sm flex items-center gap-2 hover:bg-destructive/20 transition-colors">
            <LogOut className="h-4 w-4" /> Sign Out
          </button>
        </div>
      </div>
    </AppLayout>
  );
};

export default SettingsPage;
