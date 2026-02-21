import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppInitializer from "@/components/AppInitializer";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/auth/LoginPage";
import SignupPage from "@/pages/auth/SignupPage";
import VerifyPage from "@/pages/auth/VerifyPage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import CameraGuidelinesPage from "@/pages/camera/CameraGuidelinesPage";
import CameraRecordPage from "@/pages/camera/CameraRecordPage";
import VideoPreviewPage from "@/pages/camera/VideoPreviewPage";
import PhotoCapturePage from "@/pages/photo/PhotoCapturePage";
import PhotoConfirmPage from "@/pages/photo/PhotoConfirmPage";
import ActionSelectPage from "@/pages/complaint/ActionSelectPage";
import ComplaintStatusPage from "@/pages/complaint/ComplaintStatusPage";
import HistoryPage from "@/pages/history/HistoryPage";
import RewardsPage from "@/pages/rewards/RewardsPage";
import WalletPage from "@/pages/wallet/WalletPage";
import SettingsPage from "@/pages/settings/SettingsPage";
import NotFound from "@/pages/NotFound";
import OwnerComplaintsPage from "./pages/owner/OwnerComplaintsPage";
import OwnerByPlatePage from "@/pages/owner/OwnerByPlatePage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppInitializer>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify" element={<VerifyPage />} />

            {/* Routes that require Aadhaar verification */}
            <Route path="/dashboard" element={<ProtectedRoute requireVerified={true}><DashboardPage /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute requireVerified={true}><HistoryPage /></ProtectedRoute>} />
            <Route path="/rewards" element={<ProtectedRoute requireVerified={true}><RewardsPage /></ProtectedRoute>} />
            <Route path="/wallet" element={<ProtectedRoute requireVerified={true}><WalletPage /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute requireVerified={true}><SettingsPage /></ProtectedRoute>} />
            <Route path="/owner/complaints" element={<ProtectedRoute requireVerified={true}><OwnerComplaintsPage /></ProtectedRoute>} />
            <Route path="/owner/by-plate/:plate" element={<ProtectedRoute requireVerified={true}><OwnerByPlatePage /></ProtectedRoute>} />

            {/* Routes that don't require Aadhaar verification (but require login) */}
            <Route path="/camera" element={<ProtectedRoute requireVerified={false}><CameraGuidelinesPage /></ProtectedRoute>} />
            
            <Route path="/camera/preview" element={<ProtectedRoute requireVerified={false}><VideoPreviewPage /></ProtectedRoute>} />
            <Route path="/photo-capture" element={<ProtectedRoute requireVerified={false}><PhotoCapturePage /></ProtectedRoute>} />
            <Route path="/photo-confirm" element={<ProtectedRoute requireVerified={false}><PhotoConfirmPage /></ProtectedRoute>} />
            <Route path="/camera/record" element={<ProtectedRoute requireVerified={false}><CameraRecordPage /></ProtectedRoute>} />
            <Route path="/action-select" element={<ProtectedRoute requireVerified={false}><ActionSelectPage /></ProtectedRoute>} />
            <Route path="/complaint/status" element={<ProtectedRoute requireVerified={false}><ComplaintStatusPage /></ProtectedRoute>} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppInitializer>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;