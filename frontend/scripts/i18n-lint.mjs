#!/usr/bin/env node
import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const cwd = process.cwd();
const frontendRoot = cwd.endsWith(`${path.sep}frontend`) ? cwd : path.resolve(cwd, 'frontend');
const localesDir = path.join(frontendRoot, 'src/locales');
const groups = new Map();

function loadJson(filePath) {
  return JSON.parse(readFileSync(filePath, 'utf8'));
}

for (const file of readdirSync(localesDir)) {
  if (!file.endsWith('.json')) continue;
  const [group, localeWithExt] = file.split('.');
  const locale = localeWithExt.replace('.json', '');
  if (!groups.has(group)) {
    groups.set(group, {});
  }
  groups.get(group)[locale] = loadJson(path.join(localesDir, file));
}

let hasErrors = false;

for (const [group, locales] of groups.entries()) {
  const source = locales.source;
  if (!source) {
    console.error(`✖ Missing source file for group "${group}"`);
    hasErrors = true;
    continue;
  }
  for (const locale of ['ru', 'uz']) {
    if (!locales[locale]) {
      console.error(`✖ Missing ${locale} locale file for group "${group}"`);
      hasErrors = true;
      continue;
    }
    const missing = Object.keys(source).filter((key) => !(key in locales[locale]));
    if (missing.length) {
      console.error(`✖ ${locale} locale missing keys in "${group}": ${missing.join(', ')}`);
      hasErrors = true;
    }
    const extra = Object.keys(locales[locale]).filter((key) => !(key in source));
    if (extra.length) {
      console.error(`✖ ${locale} locale has extra keys in "${group}": ${extra.join(', ')}`);
      hasErrors = true;
    }
  }
}

if (hasErrors) {
  process.exitCode = 1;
} else {
  console.log('✓ i18n locales are consistent');
}
