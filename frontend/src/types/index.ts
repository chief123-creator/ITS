export type VehicleType = 'two_wheeler' | 'four_wheeler' | 'truck';
export type ActionType = 'direct_call' | 'official_issue';
export type ComplaintStatus = 'pending' | 'timer_running' | 'resolved' | 'fine_applied';
export type AadhaarStatus = 'unverified' | 'pending' | 'verified' | 'rejected';
export type AccountStatus = 'active' | 'warned' | 'suspended' | 'banned';

export interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  aadhaar_number: string;
  aadhaar_status: AadhaarStatus;
  account_status: AccountStatus;
  trust_points: number;
  wallet_balance: number;
  role: 'user' | 'admin' | 'support';
  created_at: string;
}

export interface Complaint {
  id: string;
  user_id: string;
  video_url: string;
  latitude: number;
  longitude: number;
  recorded_at: string;
  vehicle_type: VehicleType;
  action_type: ActionType;
  status: ComplaintStatus;
  plate_number?: string;
  timer_end_time?: string;
  fine_amount: number;
  proof_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  amount: number;
  type: 'credit' | 'debit';
  description: string;
  created_at: string;
}

export interface Reward {
  id: string;
  points: number;
  reason: string;
  created_at: string;
}

export interface DashboardStats {
  totalReports: number;
  activeIssues: number;
  rewards: number;
  successRate: number;
  trustScore: number;
}
