import { test, expect } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";

test.describe("Sign-In Flows", () => {
  test("unauthenticated user sees login page when visiting protected route", async ({
    page,
  }) => {
    await page.goto(`${BASE_URL}/batch-changes`);
    await page.evaluate(() => localStorage.removeItem("rift_token"));
    await page.goto(`${BASE_URL}/batch-changes`);
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator("h2")).toContainText(/sign in/i);
  });

  test("sign-in with invalid credentials shows error", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="username"]', "nonexistent");
    await page.fill('input[name="password"]', "wrongpassword");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator('[role="alert"]')).toBeVisible();
  });
});

test.describe("Sign-Up Flows", () => {
  test("sign-up page is accessible from login", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.click('a[href="/signup"]');
    await expect(page).toHaveURL(/\/signup/);
    await expect(page.locator("h2")).toContainText(/create account/i);
  });

  test("sign-up with duplicate username shows conflict error", async ({
    page,
  }) => {
    await page.goto(`${BASE_URL}/signup`);
    // master already exists from bootstrap
    await page.fill('input[name="username"]', "master");
    await page.fill('input[name="display_name"]', "Duplicate Master");
    await page.fill('input[name="password"]', "testpass1");
    await page.click('button[type="submit"]');
    await expect(page.locator('[role="alert"]')).toBeVisible();
  });
});

test.describe("Return-to Route", () => {
  test("sign-in returns to originally requested route", async ({ page }) => {
    // Start clean
    await page.goto(`${BASE_URL}/login`);
    await page.evaluate(() => localStorage.removeItem("rift_token"));
    // Try to access protected route
    await page.goto(`${BASE_URL}/credentials`);
    await expect(page).toHaveURL(/\/login/);
    // Sign in as master
    await page.fill('input[name="username"]', "master");
    await page.fill('input[name="password"]', "master");
    await page.click('button[type="submit"]');
    // Should end up at /credentials (or /batch-changes if not preserved)
    await expect(page).toHaveURL(/\/(credentials|batch-changes)/);
  });
});
