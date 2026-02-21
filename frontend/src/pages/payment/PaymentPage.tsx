import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Loader2, CreditCard, CheckCircle2 } from 'lucide-react';

declare global {
  interface Window {
    Razorpay: any;
  }
}

const PaymentPage = () => {
  const [searchParams] = useSearchParams();
  const complaintId = searchParams.get('complaint_id');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handlePayment = async () => {
    if (!complaintId) {
      setError('Complaint ID missing');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Create Razorpay order
      const orderData = await api.createPaymentOrder(complaintId);
      
      // Razorpay options
      const options = {
        key: 'rzp_test_SGwCPPeRjTyXpt', // Your Razorpay key from .env
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'TrafficGuard',
        description: 'Challan Payment',
        order_id: orderData.order_id,
        handler: async function (response: any) {
          try {
            // Send payment success to backend
            await api.processPaymentSuccess({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              complaint_id: complaintId,
              amount: orderData.amount
            });
            
            setSuccess(true);
            setLoading(false);
          } catch (err: any) {
            setError('Payment verification failed: ' + err.message);
            setLoading(false);
          }
        },
        prefill: {
          name: 'Test User',
          email: 'test@example.com',
          contact: '9999999999'
        },
        theme: {
          color: '#8B5CF6'
        },
        modal: {
          ondismiss: function() {
            setLoading(false);
          }
        }
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err: any) {
      setError('Failed to create payment order: ' + err.message);
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="max-w-md w-full p-8 text-center">
          <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-foreground mb-2">Payment Successful!</h1>
          <p className="text-muted-foreground mb-6">
            Your challan has been paid successfully. The reporter has received their reward.
          </p>
          <Button onClick={() => window.location.href = '/'}>
            Go to Home
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full p-8">
        <div className="text-center mb-6">
          <CreditCard className="h-12 w-12 text-primary mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-foreground mb-2">Pay Challan</h1>
          <p className="text-muted-foreground">
            Complaint ID: {complaintId || 'Not provided'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
            {error}
          </div>
        )}

        <Button 
          onClick={handlePayment} 
          disabled={loading || !complaintId}
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            'Pay with Razorpay'
          )}
        </Button>

        <p className="text-xs text-muted-foreground text-center mt-4">
          Test Mode: Use card 4111 1111 1111 1111, CVV: 123
        </p>
      </Card>
    </div>
  );
};

export default PaymentPage;
