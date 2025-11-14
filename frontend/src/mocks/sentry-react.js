// Fallback mock for optional Sentry integration in local environments where the
// dependency is not installed. Each export mirrors the real API surface used
// within the application but performs no work.
const noop = () => {};

export const init = noop;

export const browserTracingIntegration = () => ({
  tracePropagationTargets: [],
});

export const profilerIntegration = () => ({});

export default {
  init,
  browserTracingIntegration,
  profilerIntegration,
};
