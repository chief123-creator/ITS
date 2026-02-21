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
import ActionSelectPage from "@/pages/complaint/ActionSelectPage";
import ComplaintStatusPage from "@/pages/complaint/ComplaintStatusPage";
import HistoryPage from "@/pages/history/HistoryPage";
import RewardsPage from "@/pages/rewards/RewardsPage";
import WalletPage from "@/pages/wallet/WalletPage";
import SettingsPage from "@/pages/settings/SettingsPage";
import NotFound from "@/pages/NotFound";

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

            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/rewards" element={<RewardsPage />} />
              <Route path="/wallet" element={<WalletPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            <Route element={<ProtectedRoute requireVerified={false} />}>
              <Route path="/camera" element={<CameraGuidelinesPage />} />
              <Route path="/camera/record" element={<CameraRecordPage />} />
              <Route path="/camera/preview" element={<VideoPreviewPage />} />
              <Route path="/action-select" element={<ActionSelectPage />} />
              <Route path="/complaint/status" element={<ComplaintStatusPage />} />
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppInitializer>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
