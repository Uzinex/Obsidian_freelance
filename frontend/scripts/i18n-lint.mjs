#!/usr/bin/env node
import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const cwd = process.cwd();
const frontendRoot = cwd.endsWith(`${path.sep}frontend`) ? cwd : path.resolve(cwd, 'frontend');
const localesDir = path.join(frontendRoot, 'src/locales');
const groups = new Map();
const sourceKeys = new Map();

function loadJson(filePath) {
  return JSON.parse(readFileSync(filePath, 'utf8'));
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function walkDir(dirPath) {
  const entries = readdirSync(dirPath);
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry);
    const stats = statSync(fullPath);
    if (stats.isDirectory()) {
      files.push(...walkDir(fullPath));
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

for (const file of readdirSync(localesDir)) {
  if (!file.endsWith('.json')) continue;
  const [group, localeWithExt] = file.split('.');
  const locale = localeWithExt.replace('.json', '');
  if (!groups.has(group)) {
    groups.set(group, {});
  }
  const jsonPath = path.join(localesDir, file);
  const payload = loadJson(jsonPath);
  groups.get(group)[locale] = payload;
  if (locale === 'source') {
    sourceKeys.set(
      group,
      new Set(Object.keys(payload)),
    );
  }
}

let hasErrors = false;
const unusedKeyReport = [];

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

const allSourceKeys = new Set(
  Array.from(sourceKeys.values()).flatMap((set) => Array.from(set)),
);

if (allSourceKeys.size) {
  const srcDir = path.join(frontendRoot, 'src');
  const filesToScan = walkDir(srcDir).filter(
    (filePath) => !filePath.includes(`${path.sep}locales${path.sep}`),
  );
  const escapedKeys = Array.from(allSourceKeys).map(escapeRegex);
  const chunkSize = 200;
  const keyChunks = [];
  for (let i = 0; i < escapedKeys.length; i += chunkSize) {
    keyChunks.push(escapedKeys.slice(i, i + chunkSize));
  }
  const usedKeys = new Set();
  for (const filePath of filesToScan) {
    const content = readFileSync(filePath, 'utf8');
    for (const chunk of keyChunks) {
      const regex = new RegExp(`(?:${chunk.join('|')})`, 'g');
      const matches = content.match(regex);
      if (matches) {
        matches.forEach((match) => usedKeys.add(match));
      }
    }
  }

  for (const [group, keys] of sourceKeys.entries()) {
    const unused = Array.from(keys).filter((key) => !usedKeys.has(key));
    if (unused.length) {
      unusedKeyReport.push({ group, unused });
    }
  }
}

if (unusedKeyReport.length) {
  const behavior = process.env.I18N_UNUSED_BEHAVIOR === 'error' ? 'error' : 'warn';
  for (const { group, unused } of unusedKeyReport) {
    const message = `⚠ ${unused.length} unused keys in "${group}": ${unused.join(', ')}`;
    if (behavior === 'error') {
      console.error(message);
      hasErrors = true;
    } else {
      console.warn(message);
    }
  }
}

if (hasErrors) {
  process.exitCode = 1;
} else {
  console.log('✓ i18n locales are consistent');
}
