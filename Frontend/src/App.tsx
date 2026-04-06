import { useState, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';
import { LoginScreen } from './components/LoginScreen';
import { HomeScreen } from './components/HomeScreen';
import { MapScreen } from './components/MapScreen';
import { SearchDocumentScreen } from './components/SearchDocumentScreen';
import { SubmitDocumentScreen } from './components/SubmitDocumentScreen';
import { NotificationScreen } from './components/NotificationScreen';
import { EvaluationScreen } from './components/EvaluationScreen';
import { AnalyticsScreen } from './components/AnalyticsScreen';
import { ChatbotScreen } from './components/ChatbotScreen';
import { SettingsScreen } from './components/SettingsScreen';
import { ForgotPasswordScreen } from './components/ForgotPasswordScreen';
import { RegisterScreen } from './components/RegisterScreen';
import { AccountDetailScreen } from './components/AccountDetailScreen';
import { DocumentCatalogScreen } from './components/DocumentCatalogScreen';
import { DocumentDetailScreen } from './components/DocumentDetailScreen';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppointmentCalendarScreen } from './components/AppointmentCalendarScreen';
import { AppointmentScreen } from './components/AppointmentScreen';
import { QueueScreen } from './components/QueueScreen';
import { QueueDisplayScreen } from './components/QueueDisplayScreen';
import { QueueStaffScreen } from './components/QueueStaffScreen';
import { AdminDashboardScreen } from './components/AdminDashboardScreen';

/* Screens where the chatbot FAB should NOT appear */
const NO_FAB_SCREENS = ['login', 'register', 'forgot-password', 'chatbot', 'queue-display'];

function AppContent() {
  const [currentScreen, setCurrentScreen] = useState('home');
  const [screenParams, setScreenParams] = useState<any>(null);
  const { isAuthenticated, isLoading, logout } = useAuth();

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  useEffect(() => {}, [isAuthenticated, isLoading]);

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
    
    // Skip auth check — bypass login for now

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
            agencyId={screenParams?.agencyId || 'default'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công'}
          />
        );
      case 'queue-display':
        return (
          <QueueDisplayScreen
            onNavigate={handleNavigate}
            agencyId={screenParams?.agencyId || 'default'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công tỉnh Thanh Hóa'}
          />
        );
      case 'queue-staff':
        return (
          <QueueStaffScreen
            onNavigate={handleNavigateWithParams}
            agencyId={screenParams?.agencyId || 'default'}
            agencyName={screenParams?.agencyName || 'Trung tâm Hành chính công'}
          />
        );
      case 'admin':
        return <AdminDashboardScreen onNavigate={handleNavigateWithParams} />;
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