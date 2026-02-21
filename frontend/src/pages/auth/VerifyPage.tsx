import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CreditCard, KeyRound, ArrowLeft, ArrowRight, Shield, CheckCircle2 } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AuthLayout from '@/components/AuthLayout';

const VerifyPage = () => {
  const navigate = useNavigate();
  const { user, sendOtp, verifyOtp, isLoading } = useAppStore();
  const [step, setStep] = useState(1);
  const [aadhaar, setAadhaar] = useState(user?.aadhaar_number || '');
  const [otp, setOtp] = useState('');
  const [testOtp, setTestOtp] = useState('');
  const [localError, setLocalError] = useState('');

  if (user?.aadhaar_status === 'verified') {
    navigate('/dashboard');
    return null;
  }

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    if (aadhaar.length !== 12) {
      setLocalError('Aadhaar must be 12 digits');
      return;
    }
    try {
      const receivedOtp = await sendOtp(aadhaar);
      setTestOtp(receivedOtp || '');
      setStep(2);
      console.log('🔐 OTP:', receivedOtp);
    } catch (err: any) {
      setLocalError(err.message);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    if (otp.length !== 6) {
      setLocalError('OTP must be 6 digits');
      return;
    }
    try {
      await verifyOtp(aadhaar, otp);
      navigate('/dashboard');
    } catch (err: any) {
      setLocalError(err.message);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-2xl font-bold text-foreground mb-1">Verify Identity</h2>
      <p className="text-muted-foreground mb-6">Complete Aadhaar verification to start reporting</p>

      {/* Progress */}
      <div className="flex items-center gap-3 mb-8">
        {[1, 2].map((s) => (
          <div key={s} className="flex items-center gap-2 flex-1">
            <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium ${
              s <= step ? 'gradient-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
            }`}>
              {s < step ? <CheckCircle2 className="h-4 w-4" /> : s}
            </div>
            <span className="text-xs text-muted-foreground hidden sm:block">
              {s === 1 ? 'Aadhaar' : 'OTP'}
            </span>
            {s === 1 && <div className={`flex-1 h-0.5 ${step > 1 ? 'gradient-primary' : 'bg-muted'}`} />}
          </div>
        ))}
      </div>

      {localError && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm"
        >
          {localError}
        </motion.div>
      )}

      {step === 1 ? (
        <form onSubmit={handleSendOtp} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-1.5 block">Aadhaar Number</label>
            <div className="relative">
              <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input type="text" value={aadhaar} onChange={(e) => setAadhaar(e.target.value.replace(/\D/g, '').slice(0, 12))}
                placeholder="Enter 12-digit Aadhaar" required maxLength={12}
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-input bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm font-mono tracking-wider" />
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 rounded-lg gradient-primary text-primary-foreground font-medium text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {isLoading ? <Shield className="h-4 w-4 animate-spin" /> : <>Send OTP <ArrowRight className="h-4 w-4" /></>}
          </button>
        </form>
      ) : (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          {testOtp && (
            <div className="mb-4 p-3 rounded-lg bg-success/10 border border-success/20">
              <p className="text-xs text-muted-foreground mb-1">Test OTP (dev only)</p>
              <p className="font-mono text-lg font-bold text-success tracking-widest">{testOtp}</p>
            </div>
          )}
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Enter OTP</label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="6-digit OTP" required maxLength={6}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-input bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm font-mono tracking-[0.5em] text-center" />
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-lg gradient-primary text-primary-foreground font-medium text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {isLoading ? <Shield className="h-4 w-4 animate-spin" /> : <>Verify <CheckCircle2 className="h-4 w-4" /></>}
            </button>
            <button
              type="button"
              onClick={() => {
                setStep(1);
                setLocalError('');
              }}
              className="w-full py-2 text-sm text-muted-foreground hover:text-foreground flex items-center justify-center gap-1"
            >
              <ArrowLeft className="h-3 w-3" /> Back
            </button>
          </form>
        </motion.div>
      )}
    </AuthLayout>
  );
};

export default VerifyPage;
