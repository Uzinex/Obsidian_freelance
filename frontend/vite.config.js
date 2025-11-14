import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

let sentryVitePlugin;
try {
  ({ default: sentryVitePlugin } = require('@sentry/vite-plugin'));
} catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') {
    throw error;
  }
}

const hasSentryConfig =
  Boolean(process.env.SENTRY_ORG) &&
  Boolean(process.env.SENTRY_PROJECT) &&
  Boolean(process.env.SENTRY_AUTH_TOKEN);

const sentryPlugin = hasSentryConfig && sentryVitePlugin
  ? [
      sentryVitePlugin({
        org: process.env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT,
        authToken: process.env.SENTRY_AUTH_TOKEN,
        telemetry: false,
      }),
    ]
  : [];

export default defineConfig({
  plugins: [react(), ...sentryPlugin],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
