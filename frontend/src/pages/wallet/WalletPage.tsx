import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wallet, ArrowUpRight, ArrowDownLeft, IndianRupee, Loader2, CheckCircle2, CreditCard, Plus, Trash2, Star } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/AppLayout';

const WalletPage = () => {
  const { balance, transactions, getBalance, getTransactions, isLoading } = useAppStore();
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawing, setWithdrawing] = useState(false);
  const [success, setSuccess] = useState(false);
  
  // Payment Methods State
  const [paymentMethods, setPaymentMethods] = useState<any[]>([]);
  const [showAddMethod, setShowAddMethod] = useState(false);
  const [methodType, setMethodType] = useState<'UPI' | 'BANK'>('UPI');
  const [upiId, setUpiId] = useState('');
  const [accountHolder, setAccountHolder] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [ifscCode, setIfscCode] = useState('');
  const [bankName, setBankName] = useState('');
  const [addingMethod, setAddingMethod] = useState(false);

  useEffect(() => {
    getBalance();
    getTransactions();
    loadPaymentMethods();
  }, [getBalance, getTransactions]);

  const loadPaymentMethods = async () => {
    try {
      const methods = await api.getPaymentMethods();
      setPaymentMethods(methods);
    } catch (error) {
      console.error('Failed to load payment methods:', error);
    }
  };

  const handleAddPaymentMethod = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingMethod(true);
    try {
      const data: any = { method_type: methodType };
      if (methodType === 'UPI') {
        data.upi_id = upiId;
      } else {
        data.account_holder_name = accountHolder;
        data.account_number = accountNumber;
        data.ifsc_code = ifscCode;
        data.bank_name = bankName;
      }
      await api.addPaymentMethod(data);
      await loadPaymentMethods();
      setShowAddMethod(false);
      // Reset form
      setUpiId('');
      setAccountHolder('');
      setAccountNumber('');
      setIfscCode('');
      setBankName('');
    } catch (error) {
      console.error('Failed to add payment method:', error);
    } finally {
      setAddingMethod(false);
    }
  };

  const handleDeleteMethod = async (id: string) => {
    try {
      await api.deletePaymentMethod(id);
      await loadPaymentMethods();
    } catch (error) {
      console.error('Failed to delete payment method:', error);
    }
  };

  const handleSetPrimary = async (id: string) => {
    try {
      await api.setPrimaryPaymentMethod(id);
      await loadPaymentMethods();
    } catch (error) {
      console.error('Failed to set primary method:', error);
    }
  };

  const handleWithdraw = async (e: React.FormEvent) => {
    e.preventDefault();
    const amount = Number(withdrawAmount);
    if (!amount || amount <= 0 || (balance && amount > balance)) return;
    setWithdrawing(true);
    
    try {
      // Convert rupees to paisa for API
      const amountInPaisa = amount * 100;
      await api.requestWithdraw(amountInPaisa);
      setSuccess(true);
      setWithdrawAmount('');
      // Refresh balance and transactions
      getBalance();
      getTransactions();
      setTimeout(() => setSuccess(false), 3000);
    } catch (error: any) {
      console.error('Withdrawal failed:', error);
      // Show error to user
    } finally {
      setWithdrawing(false);
    }
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
            <IndianRupee className="h-8 w-8" />{balance ? (balance / 100).toLocaleString() : '0'}
          </p>
        </motion.div>

        {/* Withdraw */}
        <div className="bg-card rounded-2xl border border-border p-6 mb-8">
          <h2 className="font-semibold text-foreground mb-4">Request Withdrawal</h2>
          
          {/* Payment Methods */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-foreground">Payment Methods</h3>
              <button onClick={() => setShowAddMethod(!showAddMethod)}
                className="text-xs text-primary hover:underline flex items-center gap-1">
                <Plus className="h-3 w-3" /> Add Method
              </button>
            </div>

            {/* Add Payment Method Form */}
            {showAddMethod && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                className="mb-4 p-4 rounded-lg border border-border bg-muted/30">
                <form onSubmit={handleAddPaymentMethod} className="space-y-3">
                  <div className="flex gap-2">
                    <button type="button" onClick={() => setMethodType('UPI')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        methodType === 'UPI' ? 'bg-primary text-primary-foreground' : 'bg-background text-muted-foreground'
                      }`}>
                      UPI
                    </button>
                    <button type="button" onClick={() => setMethodType('BANK')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        methodType === 'BANK' ? 'bg-primary text-primary-foreground' : 'bg-background text-muted-foreground'
                      }`}>
                      Bank Account
                    </button>
                  </div>

                  {methodType === 'UPI' ? (
                    <input type="text" value={upiId} onChange={(e) => setUpiId(e.target.value)}
                      placeholder="Enter UPI ID (e.g., user@paytm)" required
                      className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground text-sm" />
                  ) : (
                    <>
                      <input type="text" value={accountHolder} onChange={(e) => setAccountHolder(e.target.value)}
                        placeholder="Account Holder Name" required
                        className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground text-sm" />
                      <input type="text" value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)}
                        placeholder="Account Number" required
                        className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground text-sm" />
                      <input type="text" value={ifscCode} onChange={(e) => setIfscCode(e.target.value)}
                        placeholder="IFSC Code" required
                        className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground text-sm" />
                      <input type="text" value={bankName} onChange={(e) => setBankName(e.target.value)}
                        placeholder="Bank Name" required
                        className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground text-sm" />
                    </>
                  )}

                  <div className="flex gap-2">
                    <button type="submit" disabled={addingMethod}
                      className="flex-1 py-2 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50">
                      {addingMethod ? 'Adding...' : 'Add'}
                    </button>
                    <button type="button" onClick={() => setShowAddMethod(false)}
                      className="px-4 py-2 rounded-lg border border-border text-sm">
                      Cancel
                    </button>
                  </div>
                </form>
              </motion.div>
            )}

            {/* Payment Methods List */}
            <div className="space-y-2">
              {paymentMethods.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">
                  No payment methods added. Add one to withdraw funds.
                </p>
              ) : (
                paymentMethods.map((method) => (
                  <div key={method.id} className="flex items-center justify-between p-3 rounded-lg border border-border bg-background">
                    <div className="flex items-center gap-3">
                      <CreditCard className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium text-foreground flex items-center gap-2">
                          {method.method_type === 'UPI' ? method.upi_id : `${method.bank_name} - ${method.masked_account_number}`}
                          {method.is_primary && <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />}
                        </p>
                        <p className="text-xs text-muted-foreground">{method.method_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {!method.is_primary && (
                        <button onClick={() => handleSetPrimary(method.id)}
                          className="text-xs text-primary hover:underline">
                          Set Primary
                        </button>
                      )}
                      <button onClick={() => handleDeleteMethod(method.id)}
                        className="p-1 hover:bg-destructive/10 rounded">
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

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
                placeholder="Enter amount" min={0} max={balance ? balance / 100 : undefined}
                disabled={!balance || balance === 0}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm disabled:opacity-50 disabled:cursor-not-allowed" />
            </div>
            <button type="submit" disabled={withdrawing || !withdrawAmount || paymentMethods.length === 0 || !balance || balance === 0}
              className="px-6 py-2.5 rounded-xl gradient-primary text-primary-foreground font-medium text-sm flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50">
              {withdrawing ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Withdraw'}
            </button>
          </form>
          {paymentMethods.length === 0 && (
            <p className="text-xs text-muted-foreground mt-2">Add a payment method to withdraw funds</p>
          )}
          {balance === 0 && (
            <p className="text-xs text-muted-foreground mt-2">Insufficient balance to withdraw</p>
          )}
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
                  {t.type === 'credit' ? '+' : '-'}₹{(t.amount / 100).toFixed(2)}
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
