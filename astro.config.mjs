// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readFileSync, existsSync } from 'node:fs';

const LASTMOD = existsSync('./src/data/lastmod.json') ? JSON.parse(readFileSync('./src/data/lastmod.json', 'utf8')) : {};

export default defineConfig({
  site: 'https://liverpoolemergencyplumber.co.uk',
  trailingSlash: 'never',
  build: {
    format: 'file',
    // Inline CSS so the first paint is not blocked by a stylesheet request (most visits are one page).
    inlineStylesheets: 'always',
  },
  integrations: [sitemap({
    filter: (page) => !page.includes('/privacy') && !page.includes('/404'),
    serialize(item) {
      const path = new URL(item.url).pathname.replace(/\/$/, '') || '/';
      if (LASTMOD[path]) item.lastmod = LASTMOD[path];
      return item;
    },
  })],
});