import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import ssgConfig from '../ssg.config.mjs';
import { publicContent } from '../src/mocks/publicContent.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, '../dist');
const ssrDir = path.resolve(__dirname, '../dist-ssr');
const templatePath = path.join(distDir, 'index.html');
const templateRaw = await readFile(templatePath, 'utf-8');
const template = templateRaw.replace('<title>Obsidian Freelance</title>', '');
const serverEntry = path.join(ssrDir, 'ssg-entry.js');
const { render } = await import(pathToFileURL(serverEntry));

function sanitizePath(segment) {
  return segment.replace(/^\/+/, '').replace(/\/+$/, '');
}

function resolveLocalizedPath(locale, routePath) {
  if (routePath === '/') {
    return `/${locale}`;
  }
  return `/${locale}${routePath}`.replace(/\/+/g, '/');
}

const routes = [];
ssgConfig.staticRoutes.forEach((route) => {
  ssgConfig.locales.forEach((locale) => {
    routes.push({
      locale,
      path: resolveLocalizedPath(locale, route.path),
      revalidate: route.revalidate,
    });
  });
});

ssgConfig.dynamicRoutes.forEach((route) => {
  ssgConfig.locales.forEach((locale) => {
    const slugs = route.source(locale, publicContent[locale]);
    slugs.forEach((slug) => {
      const resolved = route.pattern.replace(':slug', slug);
      routes.push({
        locale,
        path: resolveLocalizedPath(locale, resolved),
        revalidate: route.revalidate,
      });
    });
  });
});

for (const target of routes) {
  const url = target.path;
  const { html, head } = await render(url);
  const pageHtml = template
    .replace('<div id="root"></div>', `<div id="root">${html}</div>`)
    .replace('</head>', `${head}\n</head>`);
  const outputDir = path.join(distDir, sanitizePath(url));
  await mkdir(outputDir, { recursive: true });
  await writeFile(path.join(outputDir, 'index.html'), pageHtml, 'utf-8');
  console.log(`SSG ✔ ${url} (ISR: ${target.revalidate})`);
}
