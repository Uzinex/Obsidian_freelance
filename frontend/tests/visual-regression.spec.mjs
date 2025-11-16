import { test, expect } from '@playwright/test';
import config from './visual-regression.config.mjs';

const { locales, viewports, pages } = config;

for (const locale of locales) {
  for (const viewport of viewports) {
    for (const pageConfig of pages) {
      test(`visual ${locale} ${pageConfig.name} ${viewport.label}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto(`http://localhost:5173/${locale}${pageConfig.path}`);
        await expect(page).toHaveScreenshot(
          `${locale}-${pageConfig.name}-${viewport.label}.png`,
          {
            animations: 'disabled',
            fullPage: true,
            maxDiffPixelRatio: 0.01,
          },
        );
      });
    }
  }
}
