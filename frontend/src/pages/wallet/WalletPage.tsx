import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wallet, ArrowUpRight, ArrowDownLeft, IndianRupee, Loader2, CheckCircle2 } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const WalletPage = () => {
  const { balance, transactions, getBalance, getTransactions, isLoading } = useAppStore();
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawing, setWithdrawing] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    getBalance();
    getTransactions();
  }, [getBalance, getTransactions]);

  const handleWithdraw = async (e: React.FormEvent) => {
    e.preventDefault();
    const amount = Number(withdrawAmount);
    if (!amount || amount <= 0 || (balance && amount > balance)) return;
    setWithdrawing(true);
    // Simulate API call - in production, you'd call a store method
    await new Promise((r) => setTimeout(r, 1500));
    setWithdrawing(false);
    setSuccess(true);
    setWithdrawAmount('');
    setTimeout(() => setSuccess(false), 3000);
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-6">Wallet</h1>

        {/* Balance */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="gradient-dark rounded-2xl p-8 mb-8 text-center">
          <Wallet className="h-8 w-8 text-primary-foreground/70 mx-auto mb-3" />
          <p className="text-sm text-primary-foreground/60 mb-1">Available Balance</p>
          <p className="text-4xl font-bold text-primary-foreground flex items-center justify-center gap-1">
            <IndianRupee className="h-8 w-8" />{balance.toLocaleString()}
          </p>
        </motion.div>

        {/* Withdraw */}
        <div className="bg-card rounded-2xl border border-border p-6 mb-8">
          <h2 className="font-semibold text-foreground mb-4">Request Withdrawal</h2>
          {success && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="mb-4 p-3 rounded-lg bg-success/10 border border-success/20 text-success text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" /> Withdrawal request submitted successfully!
            </motion.div>
          )}
          <form onSubmit={handleWithdraw} className="flex gap-3">
            <div className="relative flex-1">
              <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input type="number" value={withdrawAmount} onChange={(e) => setWithdrawAmount(e.target.value)}
                placeholder="Enter amount" min={1} max={balance}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm" />
            </div>
            <button type="submit" disabled={withdrawing || !withdrawAmount}
              className="px-6 py-2.5 rounded-xl gradient-primary text-primary-foreground font-medium text-sm flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50">
              {withdrawing ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Withdraw'}
            </button>
          </form>
        </div>

        {/* Transactions */}
        <div className="bg-card rounded-2xl border border-border p-6">
          <h2 className="font-semibold text-foreground mb-4">Recent Transactions</h2>
          <div className="space-y-3">
            {transactions.map((t) => (
              <div key={t.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                    t.type === 'credit' ? 'bg-success/10' : 'bg-destructive/10'
                  }`}>
                    {t.type === 'credit'
                      ? <ArrowDownLeft className="h-4 w-4 text-success" />
                      : <ArrowUpRight className="h-4 w-4 text-destructive" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{t.description}</p>
                    <p className="text-xs text-muted-foreground">{new Date(t.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <span className={`text-sm font-bold ${t.type === 'credit' ? 'text-success' : 'text-destructive'}`}>
                  {t.type === 'credit' ? '+' : '-'}₹{t.amount}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default WalletPage;
