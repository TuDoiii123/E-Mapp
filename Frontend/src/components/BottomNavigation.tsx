import { Home, FileText, MessageCircle, BarChart3, Settings } from 'lucide-react';
import { Badge } from './ui/badge';
import React from 'react';
interface BottomNavigationProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
}

export function BottomNavigation({ currentScreen, onNavigate }: BottomNavigationProps) {
  const navItems = [
    {
      id: 'home',
      label: 'Trang chủ',
      icon: Home
    },
    {
      id: 'search',
      label: 'Hồ sơ',
      icon: FileText
    },
    {
      id: 'chatbot',
      label: 'Trợ lý AI',
      icon: MessageCircle
    },
    {
      id: 'analytics',
      label: 'Phân tích',
      icon: BarChart3
    },
    {
      id: 'settings',
      label: 'Cài đặt',
      icon: Settings
    }
  ];

  // Don't show navigation on login, register, forgot-password screens
  if (['login', 'register', 'forgot-password', 'account-detail'].includes(currentScreen)) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom">
      <div className="flex items-center justify-around px-2 py-2">
        {navItems.map((item) => {
          const isActive = currentScreen === item.id;
          const Icon = item.icon;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center justify-center p-2 rounded-lg transition-colors min-w-0 flex-1 ${
                isActive 
                  ? 'text-red-600 bg-red-50' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <div className="relative">
                <Icon className="w-5 h-5" />
                {item.id === 'chatbot' && currentScreen !== 'chatbot' && (
                  <Badge variant="destructive" className="absolute -top-2 -right-2 w-2 h-2 p-0 text-xs">
                  </Badge>
                )}
              </div>
              <span className="text-xs mt-1 truncate">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}