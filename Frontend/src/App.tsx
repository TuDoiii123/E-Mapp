import { useState, useEffect } from 'react';
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
import { BottomNavigation } from './components/BottomNavigation';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppointmentCalendarScreen } from './components/AppointmentCalendarScreen';

function AppContent() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [screenParams, setScreenParams] = useState<any>(null);
  const { isAuthenticated, isLoading, logout } = useAuth();

  useEffect(() => {
    // If authenticated, go to home, otherwise go to login
    if (!isLoading) {
      if (isAuthenticated && currentScreen === 'login') {
        setCurrentScreen('home');
      } else if (!isAuthenticated && currentScreen !== 'login' && currentScreen !== 'register' && currentScreen !== 'forgot-password') {
        setCurrentScreen('login');
      }
    }
  }, [isAuthenticated, isLoading]);

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
    
    // If not logged in and trying to access a protected screen, redirect to login
    if (!isAuthenticated && !publicScreens.includes(currentScreen)) {
      return <LoginScreen onLogin={handleLogin} onNavigate={handleNavigate} />;
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
      default:
        return <HomeScreen onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="size-full min-h-screen bg-gray-50 relative">
      {/* Main Content */}
      <div className={`${isAuthenticated && !['account-detail'].includes(currentScreen) ? 'pb-16' : ''}`}>
        {renderScreen()}
      </div>
      
      {/* Bottom Navigation */}
      {isAuthenticated && (
        <BottomNavigation 
          currentScreen={currentScreen} 
          onNavigate={handleNavigate} 
        />
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