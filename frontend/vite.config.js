import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'module';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const require = createRequire(import.meta.url);

const __dirname = dirname(fileURLToPath(import.meta.url));

let sentryVitePlugin;
try {
  ({ default: sentryVitePlugin } = require('@sentry/vite-plugin'));
} catch (error) {
  if (error.code !== 'MODULE_NOT_FOUND') {
    throw error;
  }
}

const sentryAlias = {};
try {
  require.resolve('@sentry/react');
} catch (error) {
  if (error.code === 'MODULE_NOT_FOUND') {
    sentryAlias['@sentry/react'] = resolve(
      __dirname,
      'src',
      'mocks',
      'sentry-react.js',
    );
  } else {
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

const reactPlugin = react({
  fastRefresh: false,
});

export default defineConfig({
  plugins: [reactPlugin, ...sentryPlugin],
  resolve: {
    alias: {
      ...sentryAlias,
    },
  },
  build: {
    sourcemap: true,
    manifest: true,
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
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
