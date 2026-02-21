import { create } from 'zustand';
import { api } from '@/lib/api';
import type { User, Complaint } from '@/lib/api';

interface DashboardStats {
  totalReports: number;
  activeIssues: number;
  rewards: number;
  successRate: number;
  trustScore: number;
}

interface Balance {
  balance: number;
}

interface Transaction {
  id: string;
  amount: number;
  type: 'credit' | 'debit';
  description: string;
  created_at: string;
}

interface Reward {
  id: string;
  points: number;
  reason: string;
  created_at: string;
}

interface AppState {
  // User
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Current video recording
  currentVideo: {
    videoBlob: Blob;
    latitude: number;
    longitude: number;
    duration: number;
    vehicleType?: 'two_wheeler' | 'four_wheeler' | 'truck';
  } | null;

  // Current complaint
  currentComplaint: Complaint | null;

  // Plate detection
  detectedPlate: string | null;
  capturedImage: string | null;

  // Dashboard
  dashboardStats: DashboardStats | null;
  complaints: Complaint[];
  balance: number | null;
  transactions: Transaction[];
  rewards: Reward[];

  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  logout: () => void;

  // Video
  setCurrentVideo: (video: AppState['currentVideo']) => void;
  clearCurrentVideo: () => void;

  // Complaint
  setCurrentComplaint: (complaint: Complaint | null) => void;

  // Plate detection
  setDetectedPlate: (plate: string | null) => void;
  setCapturedImage: (image: string | null) => void;

  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  signup: (userData: any) => Promise<void>;
  sendOtp: (aadhaar: string) => Promise<string | undefined>;
  verifyOtp: (aadhaar: string, otp: string) => Promise<void>;

  // Complaint actions
  submitComplaint: (formData: FormData) => Promise<void>;

  // Dashboard actions
  getDashboardStats: () => Promise<void>;
  getComplaints: () => Promise<void>;
  getBalance: () => Promise<void>;
  getTransactions: () => Promise<void>;
  getRewards: () => Promise<void>;
  updateUser: (userData: Partial<User>) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  currentVideo: null,
  currentComplaint: null,
  detectedPlate: null,
  capturedImage: null,
  dashboardStats: null,
  complaints: [],
  balance: null,
  transactions: [],
  rewards: [],

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ user: null, isAuthenticated: false, currentVideo: null, currentComplaint: null });
    window.location.href = '/login';
  },

  setCurrentVideo: (video) => set({ currentVideo: video }),
  clearCurrentVideo: () => set({ currentVideo: null }),
  setCurrentComplaint: (complaint) => set({ currentComplaint: complaint }),
  setDetectedPlate: (plate) => set({ detectedPlate: plate }),
  setCapturedImage: (image) => set({ capturedImage: image }),

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.login(email, password);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      set({ user: response.user, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  signup: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.signup(userData);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      set({ user: response.user, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  sendOtp: async (aadhaar) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.sendOtp(aadhaar);
      set({ isLoading: false });
      return response.otp;
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  verifyOtp: async (aadhaar, otp) => {
    set({ isLoading: true, error: null });
    try {
      const updatedUser = await api.verifyOtp(aadhaar, otp);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      set({ user: updatedUser, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  submitComplaint: async (formData: FormData) => {
    set({ isLoading: true, error: null });
    try {
      const complaint = await api.createComplaint(formData);
      set({ currentComplaint: complaint, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  getDashboardStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const stats = await api.getDashboardStats();
      set({ dashboardStats: stats, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  getComplaints: async () => {
    set({ isLoading: true, error: null });
    try {
      const complaints = await api.getComplaints();
      set({ complaints, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  getBalance: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getBalance();
      set({ balance: data.balance, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  getTransactions: async () => {
    set({ isLoading: true, error: null });
    try {
      const transactions = await api.getTransactions();
      set({ transactions, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  getRewards: async () => {
    set({ isLoading: true, error: null });
    try {
      const rewards = await api.getRewards();
      set({ rewards, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
  },

  updateUser: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const updatedUser = await api.updateUser(userData);
      set({ user: updatedUser, isLoading: false });
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
      throw error;
    }
    
  },
  
}));