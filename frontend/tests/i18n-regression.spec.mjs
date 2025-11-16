import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

async function seedAuth(page) {
  await page.addInitScript(({ state }) => {
    window.localStorage.setItem('obsidian_freelance_auth', JSON.stringify(state));
  }, {
    state: {
      token: 'qa-token',
      user: {
        email: 'qa@obsidianfreelance.com',
        profile: {
          role: 'client',
          is_verified: true,
          staff_roles: ['staff', 'moderator'],
        },
      },
    },
  });
}

test.describe('i18n regression', () => {
  test('registration pseudo locale stretch', async ({ page }) => {
    await page.goto(`${BASE_URL}/register?locale=pseudo`);
    await expect(page.locator('h1')).toContainText('Создать аккаунт', { timeout: 10000 });
    const overflow = await page.evaluate(() => ({
      body: document.body.scrollWidth - document.body.clientWidth,
      html: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    }));
    expect(overflow.body).toBeLessThanOrEqual(2);
    expect(overflow.html).toBeLessThanOrEqual(2);
  });

  test('order dashboard ru locale', async ({ page }) => {
    await seedAuth(page);
    await page.goto(`${BASE_URL}/ru/orders`);
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('body')).toContainText('Работы');
  });

  test('profile editor ru locale', async ({ page }) => {
    await seedAuth(page);
    await page.goto(`${BASE_URL}/ru/profile`);
    await expect(page.locator('h1')).first().toBeVisible();
    await expect(page.locator('body')).toContainText('Профиль');
  });

  test('public pages render ru/uz variants', async ({ page }) => {
    await page.goto(`${BASE_URL}/ru/faq`);
    await expect(page.locator('body')).toContainText('FAQ');
    await page.goto(`${BASE_URL}/uz/blog`);
    await expect(page.locator('body')).toContainText('Blog');
  });
});
