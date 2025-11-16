import { useEffect } from 'react';

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
  useEffect(() => {
    if (typeof window === 'undefined' || !Array.isArray(targetIds) || targetIds.length === 0) {
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
              ...metadata,
            });
          }
        });
      },
      { threshold: 0.4 },
    );

    targetIds.forEach((id) => {
      const el = document.querySelector(`[data-analytics-id="${id}"]`);
      if (el) {
        observer.observe(el);
      }
    });

    return () => observer.disconnect();
  }, [targetIds.join('::'), JSON.stringify(metadata)]);
}
