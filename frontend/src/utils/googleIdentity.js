const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
let scriptPromise;

function injectScript() {
  if (scriptPromise) {
    return scriptPromise;
  }
  scriptPromise = new Promise((resolve, reject) => {
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      reject(new Error('Google Identity is not available in this environment.'));
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => resolve(window.google);
    script.onerror = (error) => reject(error);
    document.head.appendChild(script);
  });
  return scriptPromise;
}

export function loadGoogleIdentity() {
  if (!CLIENT_ID) {
    return Promise.reject(new Error('Google client ID is not configured.'));
  }
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Google Identity unavailable on the server.'));
  }
  if (window.google?.accounts?.id) {
    return Promise.resolve(window.google);
  }
  return injectScript();
}

export const GOOGLE_CLIENT_ID = CLIENT_ID;
