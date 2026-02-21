import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Camera, Sun, Car, MapPin, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';
import AppLayout from '@/components/AppLayout';

const guidelines = [
  { icon: Car, title: 'License Plate Visible', desc: 'Ensure the vehicle\'s number plate is clearly captured in the video.' },
  { icon: Sun, title: 'Good Lighting', desc: 'Record in well-lit conditions for clear evidence.' },
  { icon: MapPin, title: 'Location Access', desc: 'Allow GPS access so we can tag the exact location.' },
  { icon: Clock, title: 'Min 10 Seconds', desc: 'Record at least 10 seconds of footage for valid evidence.' },
];

const CameraGuidelinesPage = () => {
  const navigate = useNavigate();

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-2">Recording Guidelines</h1>
        <p className="text-muted-foreground mb-8">Follow these steps for a valid violation report</p>

        <motion.div initial="hidden" animate="show"
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
          className="space-y-4 mb-8">
          {guidelines.map((g, i) => (
            <motion.div key={i}
              variants={{ hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } }}
              className="flex items-start gap-4 p-4 rounded-xl bg-card border border-border">
              <div className="h-10 w-10 rounded-lg gradient-primary flex items-center justify-center shrink-0">
                <g.icon className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <p className="font-medium text-foreground">{g.title}</p>
                <p className="text-sm text-muted-foreground">{g.desc}</p>
              </div>
              <CheckCircle2 className="h-5 w-5 text-success shrink-0 mt-0.5" />
            </motion.div>
          ))}
        </motion.div>

        <button onClick={() => navigate('/camera/record')}
          className="w-full py-3 rounded-xl gradient-primary text-primary-foreground font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">
          <Camera className="h-5 w-5" /> Start Recording <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </AppLayout>
  );
};

export default CameraGuidelinesPage;
