import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Phone, User, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';

export default function OwnerByPlatePage() {
  const { plate } = useParams();
  const navigate = useNavigate();
  const [owner, setOwner] = useState<{ name: string; phone: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!plate) return;
    api.getOwnerByPlate(plate)
      .then(setOwner)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [plate]);

  const handleCall = () => {
    if (owner?.phone) window.location.href = `tel:${owner.phone}`;
  };

  if (loading) return <AppLayout><div className="page-container">Loading...</div></AppLayout>;

  return (
    <AppLayout>
      <div className="page-container">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="mr-2" /> Back
        </Button>
        <div className="mt-6 bg-card p-6 rounded-xl">
          <h1 className="text-2xl font-bold mb-4">Owner for Plate {plate}</h1>
          {error && <p className="text-destructive">{error}</p>}
          {owner ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-accent/30 rounded-lg">
                <User className="w-5 h-5" />
                <span className="font-medium">{owner.name}</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-accent/30 rounded-lg">
                <Phone className="w-5 h-5" />
                <span className="font-medium">{owner.phone}</span>
              </div>
              <Button onClick={handleCall} className="w-full mt-4">
                Call Owner
              </Button>
            </div>
          ) : (
            !error && <p>Owner not found</p>
          )}
        </div>
      </div>
    </AppLayout>
  );
}