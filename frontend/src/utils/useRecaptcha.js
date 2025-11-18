import { useCallback, useEffect, useState } from 'react';

const SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY;

function loadRecaptchaScript() {
  if (!SITE_KEY) {
    return Promise.resolve(false);
  }
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return Promise.resolve(false);
  }
  if (window.grecaptcha?.ready) {
    return new Promise((resolve) => {
      window.grecaptcha.ready(() => resolve(true));
    });
  }
  const existing = document.querySelector('script[data-recaptcha-script]');
  if (existing) {
    return new Promise((resolve) => {
      existing.addEventListener('load', () => {
        if (window.grecaptcha?.ready) {
          window.grecaptcha.ready(() => resolve(true));
        } else {
          resolve(false);
        }
      });
    });
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `https://www.google.com/recaptcha/api.js?render=${SITE_KEY}`;
    script.async = true;
    script.defer = true;
    script.dataset.recaptchaScript = 'true';
    script.onload = () => {
      if (window.grecaptcha?.ready) {
        window.grecaptcha.ready(() => resolve(true));
      } else {
        resolve(false);
      }
    };
    script.onerror = (error) => {
      reject(error);
    };
    document.body.appendChild(script);
  });
}

export function useRecaptcha() {
  const [ready, setReady] = useState(false);
  const isEnabled = Boolean(SITE_KEY);

  useEffect(() => {
    let cancelled = false;
    if (!isEnabled || typeof window === 'undefined') {
      setReady(false);
      return undefined;
    }
    loadRecaptchaScript()
      .then(() => {
        if (!cancelled) {
          setReady(true);
        }
      })
      .catch((error) => {
        console.error('Failed to load reCAPTCHA', error);
        if (!cancelled) {
          setReady(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [isEnabled]);

  const execute = useCallback(
    async (action = 'submit') => {
      if (!isEnabled) {
        return null;
      }
      if (!ready) {
        throw new Error('reCAPTCHA is not ready yet.');
      }
      return window.grecaptcha.execute(SITE_KEY, { action });
    },
    [ready, isEnabled],
  );

  return { execute, ready, isEnabled };
}
