import { useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';
import type { User } from '@/types';

const AppInitializer = ({ children }: { children: React.ReactNode }) => {
  const { setUser } = useAppStore();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user: User = JSON.parse(storedUser);
        setUser(user);
      } catch {
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
      }
    }
  }, [setUser]);

  return <>{children}</>;
};

export default AppInitializer;
