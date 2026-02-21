import { API_BASE_URL } from '@/config';

// Types (copy these from your types file or import)
export interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  aadhaar_number: string;
  aadhaar_status: 'unverified' | 'pending' | 'verified' | 'rejected';
  account_status: 'active' | 'warned' | 'suspended' | 'banned';
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
  vehicle_type: 'two_wheeler' | 'four_wheeler' | 'truck';
  action_type: 'direct_call' | 'official_issue';
  status: 'pending' | 'timer_running' | 'resolved' | 'fine_applied';
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

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem('token');
    const headers = new Headers(options.headers || {});
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    // Don't set Content-Type for FormData; browser sets it with boundary
    if (!(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Unauthorized – clear token and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
      }
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async signup(userData: {
    name: string;
    email: string;
    phone: string;
    aadhaar_number: string;
    password: string;
  }): Promise<{ access_token: string; user: User }> {
    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async sendOtp(aadhaar_number: string): Promise<{ message: string; otp?: string }> {
    return this.request('/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ aadhaar_number }),
    });
  }

  async verifyOtp(aadhaar_number: string, otp: string): Promise<User> {
    return this.request('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ aadhaar_number, otp }),
    });
  }

  // User
  async getCurrentUser(): Promise<User> {
    return this.request('/users/me');
  }

  async updateUser(data: Partial<User>): Promise<User> {
    return this.request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Complaints
  async createComplaint(formData: FormData): Promise<Complaint> {
    return this.request('/complaints', {
      method: 'POST',
      body: formData,
    });
  }

  async getComplaints(status?: string): Promise<Complaint[]> {
    const query = status ? `?status=${status}` : '';
    return this.request(`/complaints${query}`);
  }

  async getComplaint(id: string): Promise<Complaint> {
    return this.request(`/complaints/${id}`);
  }

  // Wallet
  async getBalance(): Promise<{ balance: number }> {
    return this.request('/wallet/balance');
  }

  async getTransactions(): Promise<Transaction[]> {
    return this.request('/wallet/transactions');
  }

  async requestWithdraw(amount: number): Promise<{ status: string }> {
    return this.request('/wallet/withdraw', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
  }

  // Rewards
  async getRewards(): Promise<Reward[]> {
    return this.request('/rewards');
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request('/dashboard/stats');
  }
}

export const api = new ApiClient(API_BASE_URL);