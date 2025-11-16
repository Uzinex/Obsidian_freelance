import path from 'node:path';

const rootDir = process.cwd().endsWith(`${path.sep}frontend`)
  ? process.cwd()
  : path.resolve(process.cwd(), 'frontend');

const config = {
  baselineDir: path.join(rootDir, 'tests/visual-baseline'),
  diffDir: path.join(rootDir, 'tests/visual-diffs'),
  locales: ['ru', 'uz'],
  viewports: [
    { label: 'desktop', width: 1440, height: 900 },
    { label: 'mobile', width: 390, height: 844 },
  ],
  pages: [
    { name: 'home', path: '/', tags: ['ssg', 'hero', 'cta'] },
    { name: 'about', path: '/about', tags: ['story', 'trust'] },
    { name: 'faq', path: '/faq', tags: ['accordion', 'structured-data'] },
    { name: 'blog-index', path: '/blog', tags: ['seo', 'listing'] },
    { name: 'blog-article', path: '/blog/enterprise-cases', tags: ['article', 'schema'] },
    { name: 'categories', path: '/categories', tags: ['skills', 'grid'] },
    { name: 'contacts', path: '/contacts', tags: ['map', 'cta'] },
    { name: 'profile', path: '/profiles/elite-team', tags: ['ssr', 'cta'] },
    { name: 'orders', path: '/orders', tags: ['app', 'filters'] },
    { name: 'profile-settings', path: '/profile', tags: ['app', 'forms'] },
  ],
};

export default config;
