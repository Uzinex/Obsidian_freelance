import { useEffect, useRef, useState } from 'react';
import { GOOGLE_CLIENT_ID, loadGoogleIdentity } from '../utils/googleIdentity.js';

export default function GoogleButton({ text = 'signup', onCredential, disabled = false }) {
  const buttonRef = useRef(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || !buttonRef.current || !onCredential) {
      return undefined;
    }
    let cancelled = false;
    let googleInstance;
    setError('');
    loadGoogleIdentity()
      .then((google) => {
        if (!google?.accounts?.id || cancelled) {
          return;
        }
        googleInstance = google.accounts.id;
        googleInstance.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response) => {
            if (response?.credential && !disabled) {
              onCredential(response.credential);
            }
          },
          ux_mode: 'popup',
        });
        googleInstance.renderButton(buttonRef.current, {
          theme: 'outline',
          size: 'large',
          shape: 'rectangular',
          text: text === 'login' ? 'signin_with' : 'signup_with',
          logo_alignment: 'left',
          width: 320,
        });
      })
      .catch((err) => {
        if (!cancelled) {
          console.error('Failed to load Google Identity Services', err);
          setError('Google недоступен.');
        }
      });
    return () => {
      cancelled = true;
      if (buttonRef.current) {
        buttonRef.current.innerHTML = '';
      }
    };
  }, [disabled, onCredential, text]);

  if (!GOOGLE_CLIENT_ID) {
    return null;
  }

  return (
    <div className={`google-button-wrapper ${disabled ? 'is-disabled' : ''}`}>
      <div ref={buttonRef} aria-live="polite" />
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
