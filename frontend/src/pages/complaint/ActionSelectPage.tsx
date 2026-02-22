import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, FileText } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

export default function ActionSelectPage() {
  const navigate = useNavigate();
  const { detectedPlate, setDetectedPlate } = useAppStore();
  const [error, setError] = useState('');
  
  useEffect(() => {
    if (!detectedPlate) {
      setDetectedPlate('MP20MN6927'); // mock plate for demo
    }
  }, []);
  
  const handleDirectCall = () => {
    navigate(`/owner/by-plate/${detectedPlate}`);
  };

  const handleOfficialIssue = () => {
    navigate('/camera/record');
  };

  return (
    <AppLayout>
      <div className="page-container space-y-6">
        <h1 className="page-title">Choose Action</h1>
        <div className="space-y-4">
          <motion.button
            onClick={handleDirectCall}
            className="w-full p-6 bg-card border-2 border-success/25 rounded-2xl text-left"
          >
            <Phone className="w-6 h-6 text-success mb-2" />
            <h3 className="font-bold text-lg">Direct Call</h3>
            <p className="text-sm text-muted-foreground">Contact owner immediately</p>
          </motion.button>
          <motion.button
            onClick={handleOfficialIssue}
            className="w-full p-6 bg-card border border-border rounded-2xl text-left"
          >
            <FileText className="w-6 h-6 text-primary mb-2" />
            <h3 className="font-bold text-lg">Official Issue</h3>
            <p className="text-sm text-muted-foreground">Start 24h timer, owner must respond</p>
          </motion.button>
        </div>
      </div>
    </AppLayout>
  );
}