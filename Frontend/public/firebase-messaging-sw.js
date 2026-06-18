// Service worker nhận push nền. Điền config Firebase web của bạn vào đây
// (service worker không đọc được biến môi trường Vite).
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: '', authDomain: '', projectId: '', messagingSenderId: '', appId: '',
});
const messaging = firebase.messaging();
messaging.onBackgroundMessage((payload) => {
  const n = (payload && payload.notification) || {};
  self.registration.showNotification(n.title || 'E-Mapp', { body: n.body || '' });
});
