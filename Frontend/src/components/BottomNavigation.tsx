import { Home, FileText, MessageCircle, Hash, Settings, ShieldCheck, MonitorPlay } from 'lucide-react';
import { Badge } from './ui/badge';
import React from 'react';
import { useAuth } from '../contexts/AuthContext';

interface BottomNavigationProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
}

export function BottomNavigation({ currentScreen, onNavigate }: BottomNavigationProps) {
  const { user } = useAuth();
  const role = (user as any)?.role || 'citizen';

  // Nav items theo role
  const citizenItems = [
    { id: 'home',    label: 'Trang chủ',  icon: Home },
    { id: 'search',  label: 'Tra cứu',    icon: FileText },
    { id: 'queue',   label: 'Hàng chờ',  icon: Hash },
    { id: 'chatbot', label: 'Trợ lý AI', icon: MessageCircle },
    { id: 'settings',label: 'Cài đặt',   icon: Settings },
  ];

  const staffItems = [
    { id: 'home',        label: 'Trang chủ',   icon: Home },
    { id: 'queue-staff', label: 'Quầy phục vụ',icon: Hash },
    { id: 'queue-display',label: 'Bảng chờ',   icon: MonitorPlay },
    { id: 'chatbot',     label: 'Trợ lý AI',   icon: MessageCircle },
    { id: 'settings',    label: 'Cài đặt',     icon: Settings },
  ];

  const adminItems = [
    { id: 'home',        label: 'Trang chủ',  icon: Home },
    { id: 'admin',       label: 'Quản trị',   icon: ShieldCheck },
    { id: 'queue-staff', label: 'Hàng chờ',  icon: Hash },
    { id: 'chatbot',     label: 'Trợ lý AI', icon: MessageCircle },
    { id: 'settings',    label: 'Cài đặt',   icon: Settings },
  ];

  const navItems =
    role === 'admin' ? adminItems :
    role === 'staff' ? staffItems :
    citizenItems;

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