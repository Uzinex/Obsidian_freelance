import { publicContent } from './src/mocks/publicContent.js';

const locales = ['ru', 'uz'];

const staticRoutes = [
  { path: '/', label: 'Landing', revalidate: '24h' },
  { path: '/how-it-works', label: 'How it works', revalidate: '24h' },
  { path: '/escrow', label: 'Escrow', revalidate: '24h' },
  { path: '/categories', label: 'Categories & skills', revalidate: '12h' },
  { path: '/faq', label: 'FAQ', revalidate: '24h' },
  { path: '/blog', label: 'Blog index', revalidate: '6h' },
  { path: '/about', label: 'About', revalidate: '24h' },
  { path: '/contacts', label: 'Contacts', revalidate: '24h' },
  { path: '/orders', label: 'Orders listing', revalidate: '2h' },
  { path: '/terms', label: 'Terms', revalidate: 'monthly' },
  { path: '/privacy', label: 'Privacy', revalidate: 'monthly' },
  { path: '/cookies', label: 'Cookies', revalidate: 'monthly' },
];

const dynamicRoutes = [
  {
    pattern: '/profiles/:slug',
    revalidate: 'weekly',
    source: (locale) => publicContent[locale].profiles.map((profile) => profile.slug),
  },
  {
    pattern: '/blog/:slug',
    revalidate: '6h',
    source: (locale) => publicContent[locale].blog.map((article) => article.slug),
  },
];

export default {
  locales,
  staticRoutes,
  dynamicRoutes,
  siteUrl: 'https://obsidianfreelance.com',
};
