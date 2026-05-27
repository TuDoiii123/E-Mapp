import { useState, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';
import { LoginScreen } from './screens/user/LoginScreen';
import { HomeScreen } from './screens/user/HomeScreen';
import { MapScreen } from './screens/user/MapScreen';
import { SearchDocumentScreen } from './screens/user/SearchDocumentScreen';
import { SubmitDocumentScreen } from './screens/user/SubmitDocumentScreen';
import { NotificationScreen } from './screens/user/NotificationScreen';
import { EvaluationScreen } from './screens/user/EvaluationScreen';
import { AnalyticsScreen } from './screens/user/AnalyticsScreen';
import { ChatbotScreen } from './screens/user/ChatbotScreen';
import { SettingsScreen } from './screens/user/SettingsScreen';
import { ForgotPasswordScreen } from './screens/user/ForgotPasswordScreen';
import { RegisterScreen } from './screens/user/RegisterScreen';
import { AccountDetailScreen } from './screens/user/AccountDetailScreen';
import { DocumentCatalogScreen } from './screens/user/DocumentCatalogScreen';
import { DocumentDetailScreen } from './screens/user/DocumentDetailScreen';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppointmentCalendarScreen } from './screens/user/AppointmentCalendarScreen';
import { AppointmentScreen } from './screens/user/AppointmentScreen';
import { QueueScreen } from './screens/user/QueueScreen';
import { QueueDisplayScreen } from './screens/user/QueueDisplayScreen';
import { QueueStaffScreen } from './screens/user/QueueStaffScreen';
import { AdminShell } from './screens/admin/AdminShell';

/* Screens where the chatbot FAB should NOT appear */
const NO_FAB_SCREENS = [
  'login', 'register', 'forgot-password', 'chatbot', 'queue-display',
  // Admin screens — no floating chatbot button
  'admin',
];

function AppContent() {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [screenParams, setScreenParams] = useState<any>(null);
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  // Lắng nghe 401 từ api.ts → tự động đăng xuất và về login
  useEffect(() => {
    const onAuthLogout = () => {
      logout();
      setCurrentScreen('login');
      setScreenParams(null);
    };
    window.addEventListener('auth:logout', onAuthLogout);
    return () => window.removeEventListener('auth:logout', onAuthLogout);
  }, [logout]);

  // Auto-redirect: admin → trang quản trị | citizen/staff → home
  useEffect(() => {
    if (!isAuthenticated || !user) return;
    if (user.role === 'admin' && currentScreen !== 'admin') {
      // Chỉ redirect khi đang ở các trang công cộng hoặc home
      if (['login', 'home', 'register', 'forgot-password'].includes(currentScreen)) {
        setCurrentScreen('admin');
        setScreenParams(null);
      }
    }
  }, [isAuthenticated, user?.role]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleLogin = () => {
    setCurrentScreen('home');
  };

  const handleNavigate = (screen: string) => {
    if (screen === 'login') {
      logout();
    }
    setCurrentScreen(screen);
    setScreenParams(null);
  };

  // enhanced navigate with params support
  const handleNavigateWithParams = (screen: string, params?: any) => {
    if (screen === 'login') {
      logout();
    }
    setCurrentScreen(screen);
    setScreenParams(params || null);
  };

  const renderScreen = () => {
    // Show loading state
    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Đang tải...</p>
          </div>
        </div>
      );
    }

    // Public screens that don't require authentication
    const publicScreens = ['login', 'forgot-password', 'register'];

    // Auth guard: redirect unauthenticated users to login
    if (!isAuthenticated && !publicScreens.includes(currentScreen)) {
      return <LoginScreen onLogin={handleLogin} onNavigate={handleNavigate} />;
    }

    // Admin guard: non-admin cannot access admin dashboard
    if (currentScreen === 'admin' && user?.role !== 'admin') {
      return <HomeScreen onNavigate={handleNavigateWithParams} />;
    }

    switch (currentScreen) {
      case 'login':
        return <LoginScreen onLogin={handleLogin} onNavigate={handleNavigate} />;
      case 'forgot-password':
        return <ForgotPasswordScreen onNavigate={handleNavigate} />;
      case 'register':
        return <RegisterScreen onNavigate={handleNavigate} />;
      case 'home':
        return <HomeScreen onNavigate={handleNavigateWithParams} />;
      case 'appointment':
        return <AppointmentCalendarScreen onNavigate={handleNavigateWithParams} />;
      case 'booking':
        return <AppointmentScreen onNavigate={handleNavigateWithParams} />;
      case 'map':
        return <MapScreen onNavigate={handleNavigate} />;
      case 'search':
        return <SearchDocumentScreen onNavigate={handleNavigate} />;
      case 'submit':
        return <SubmitDocumentScreen onNavigate={handleNavigate} />;
      case 'notifications':
        return <NotificationScreen onNavigate={handleNavigate} />;
      case 'evaluation':
        return <EvaluationScreen onNavigate={handleNavigate} />;
      case 'document-catalog':
        return <DocumentCatalogScreen onNavigate={handleNavigateWithParams} />;
      case 'document-detail':
        return <DocumentDetailScreen onNavigate={handleNavigateWithParams} serviceId={screenParams?.id} params={screenParams} />;
      case 'analytics':
        return <AnalyticsScreen onNavigate={handleNavigate} />;
      case 'chatbot':
        return <ChatbotScreen onNavigate={handleNavigate} />;
      case 'settings':
        return <SettingsScreen onNavigate={handleNavigate} />;
      case 'account-detail':
        return <AccountDetailScreen onNavigate={handleNavigate} />;
      case 'queue':
        return (
          <QueueScreen
            onNavigate={handleNavigateWithParams}
            agencyId={screenParams?.agencyId || 'ubnd-thanhhoa'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công tỉnh Thanh Hóa'}
          />
        );
      case 'queue-display':
        return (
          <QueueDisplayScreen
            onNavigate={handleNavigate}
            agencyId={screenParams?.agencyId || 'ubnd-thanhhoa'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công tỉnh Thanh Hóa'}
          />
        );
      case 'queue-staff':
        return (
          <QueueStaffScreen
            onNavigate={handleNavigateWithParams}
            agencyId={screenParams?.agencyId || 'ubnd-thanhhoa'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công'}
          />
        );
      case 'admin':
        return <AdminShell onNavigate={handleNavigateWithParams} />;
      default:
        return <HomeScreen onNavigate={handleNavigate} />;
    }
  };

  const showFab = !NO_FAB_SCREENS.includes(currentScreen);

  return (
    <div className="size-full min-h-screen relative">
      {renderScreen()}

      {/* Floating Chatbot Button */}
      {showFab && (
        <button
          onClick={() => handleNavigate('chatbot')}
          className="fixed bottom-6 right-5 z-50 w-14 h-14 bg-red-600 hover:bg-red-700 active:scale-95 text-white rounded-full shadow-lg shadow-red-600/40 flex items-center justify-center transition-all"
          aria-label="Mở trợ lý AI"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}