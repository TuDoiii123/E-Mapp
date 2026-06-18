import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, isSupported } from 'firebase/messaging';
import { registerPushToken } from '../services/notificationService';

const cfg = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
};

export async function initPush(): Promise<void> {
  // Thiếu cấu hình → bỏ qua êm (in-app vẫn chạy)
  if (!cfg.apiKey || !cfg.projectId || !(await isSupported().catch(() => false))) return;
  try {
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') return;
    const app = initializeApp(cfg);
    const messaging = getMessaging(app);
    const token = await getToken(messaging, {
      vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
    });
    if (token) await registerPushToken(token);
  } catch (e) {
    console.warn('[push] init bỏ qua:', e);
  }
}
