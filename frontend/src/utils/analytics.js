import { useEffect, useMemo } from 'react';

export function trackEvent(eventName, payload = {}) {
  if (typeof window === 'undefined') {
    return;
  }
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: eventName,
    timestamp: Date.now(),
    ...payload,
  });
}

export function trackError(eventName, error, payload = {}) {
  trackEvent(eventName, {
    level: 'error',
    message: error?.message,
    stack: error?.stack,
    ...payload,
  });
}

export function useScrollTelemetry(targetIds = [], metadata = {}) {
  const normalizedIds = useMemo(() => (Array.isArray(targetIds) ? [...targetIds] : []), [targetIds]);
  const metadataSignature = useMemo(() => JSON.stringify(metadata || {}), [metadata]);
  const metadataPayload = useMemo(() => JSON.parse(metadataSignature || '{}'), [metadataSignature]);

  useEffect(() => {
    if (typeof window === 'undefined' || normalizedIds.length === 0) {
      return () => {};
    }

    const seen = new Set();
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !seen.has(entry.target.dataset.analyticsId)) {
            seen.add(entry.target.dataset.analyticsId);
            trackEvent('section_viewport_enter', {
              section: entry.target.dataset.analyticsId,
              ...metadataPayload,
            });
          }
        });
      },
      { threshold: 0.4 },
    );

    normalizedIds.forEach((id) => {
      const el = document.querySelector(`[data-analytics-id="${id}"]`);
      if (el) {
        observer.observe(el);
      }
    });

    return () => observer.disconnect();
  }, [normalizedIds, metadataPayload]);
}
