#!/usr/bin/env node
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const cwd = process.cwd();
const frontendRoot = cwd.endsWith(`${path.sep}frontend`) ? cwd : path.resolve(cwd, 'frontend');
const configPath = path.join(frontendRoot, 'scripts/pseudolocalization.config.json');

const config = JSON.parse(readFileSync(configPath, 'utf8'));
const localesDir = path.join(frontendRoot, config.localesDir);

function expandText(value) {
  if (typeof value !== 'string') {
    return value;
  }
  const mapped = value
    .split('')
    .map((char) => config.vowelMap[char] || char)
    .join('');
  const extraLength = Math.ceil(mapped.length * config.expansionFactor);
  const padding = '～'.repeat(extraLength);
  return `${config.prefix}${mapped}${padding}${config.suffix}`;
}

for (const file of readdirSync(localesDir)) {
  if (!file.endsWith(config.sourceSuffix)) {
    continue;
  }
  const sourcePath = path.join(localesDir, file);
  const group = file.replace(config.sourceSuffix, '');
  const targetFile = `${group}.${config.targetLocale}.json`;
  const targetPath = path.join(localesDir, targetFile);
  const data = JSON.parse(readFileSync(sourcePath, 'utf8'));
  const transformed = Object.fromEntries(
    Object.entries(data).map(([key, value]) => [key, expandText(value)]),
  );
  writeFileSync(targetPath, `${JSON.stringify(transformed, null, 2)}\n`, 'utf8');
  console.log(`Generated ${targetFile}`);
}

console.log('✓ Pseudo locales refreshed');
