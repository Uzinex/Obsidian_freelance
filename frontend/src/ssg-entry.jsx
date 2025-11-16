import React from 'react';
import { renderToString } from 'react-dom/server';
import { StaticRouter } from 'react-router-dom/server';
import { HelmetProvider } from 'react-helmet-async';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';

export async function render(url) {
  const helmetContext = {};
  const app = (
    <HelmetProvider context={helmetContext}>
      <StaticRouter location={url}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </StaticRouter>
    </HelmetProvider>
  );
  const appHtml = renderToString(app);
  const { helmet } = helmetContext;
  const head = [
    helmet.title?.toString() ?? '',
    helmet.meta?.toString() ?? '',
    helmet.link?.toString() ?? '',
    helmet.script?.toString() ?? '',
  ].join('\n');
  return { html: appHtml, head }; 
}
