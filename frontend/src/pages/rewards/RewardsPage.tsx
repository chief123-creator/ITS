import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Star, TrendingUp, Zap } from 'lucide-react';
import { useAppStore } from '@/store/useAppStore';
import AppLayout from '@/components/AppLayout';

const RewardsPage = () => {
  const { rewards, getRewards } = useAppStore();

  useEffect(() => {
    getRewards();
  }, [getRewards]);

  const totalPoints = rewards.reduce((sum, r) => sum + r.points, 0);

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-foreground mb-6">Rewards</h1>

        {/* Summary */}
        <div className="grid sm:grid-cols-3 gap-4 mb-8">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className="stat-card gradient-primary rounded-2xl text-center">
            <Trophy className="h-6 w-6 mx-auto mb-2 opacity-80" />
            <p className="text-3xl font-bold">{totalPoints}</p>
            <p className="text-sm opacity-80">Total Points</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="stat-card gradient-success rounded-2xl text-center">
            <TrendingUp className="h-6 w-6 mx-auto mb-2 opacity-80" />
            <p className="text-3xl font-bold">1.5x</p>
            <p className="text-sm opacity-80">Multiplier</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="stat-card gradient-warning rounded-2xl text-center">
            <Zap className="h-6 w-6 mx-auto mb-2 opacity-80" />
            <p className="text-3xl font-bold">5</p>
            <p className="text-sm opacity-80">Streak</p>
          </motion.div>
        </div>

        {/* History */}
        <div className="bg-card rounded-2xl border border-border p-6">
          <h2 className="font-semibold text-foreground mb-4">Reward History</h2>
          <div className="space-y-3">
            {rewards.map((r) => (
              <div key={r.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg gradient-primary flex items-center justify-center">
                    <Star className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{r.reason}</p>
                    <p className="text-xs text-muted-foreground">{new Date(r.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-success">+{r.points}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default RewardsPage;
