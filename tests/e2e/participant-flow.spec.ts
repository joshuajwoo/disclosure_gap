import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function assertAccessible(page: Page) {
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
}

test.beforeEach(async ({ page }) => {
  await page.route("http://localhost:8000/**", async (route) => {
    throw new Error(
      `Synthetic demo attempted a live API request: ${route.request().url()}`,
    );
  });
  await page.goto("/");
});

test("synthetic participant flow reaches neutral trends and deletion", async ({
  page,
}) => {
  await expect(page.getByTestId("synthetic-banner")).toContainText(
    "SYNTHETIC DEMO",
  );
  await assertAccessible(page);
  await page
    .getByRole("button", { name: "Begin synthetic walkthrough" })
    .click();

  await page.getByLabel("Age range").selectOption("18_19");
  await page
    .getByLabel(/I understand this is a synthetic demonstration/)
    .check();
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(
    page.getByRole("heading", { name: "Starting point" }),
  ).toBeFocused();
  await assertAccessible(page);
  await page.getByRole("button", { name: "Save baseline" }).click();

  await page.getByLabel("What happened?").selectOption("chose_private");
  await page.getByRole("button", { name: "Save week 1" }).click();
  await page.getByLabel("What happened?").selectOption("shared");
  await page.getByRole("button", { name: "Save week 2" }).click();
  await page
    .getByLabel("Did you want to talk about a personal concern?")
    .selectOption("no");
  await expect(page.getByTestId("check-in-followups")).toHaveCount(0);
  await page.getByRole("button", { name: "Save week 3" }).click();
  await page
    .getByLabel("Did you want to talk about a personal concern?")
    .selectOption("yes");
  await page.getByLabel("What happened?").selectOption("shared");
  await page.getByRole("button", { name: "Save week 4" }).click();

  await page.getByRole("button", { name: "Complete follow-up" }).click();
  await expect(page.getByTestId("trend-summary")).toContainText(
    "In 2 of 3 check-ins where you wanted to talk",
  );
  await expect(page.getByText(/not a diagnosis, risk estimate/)).toBeVisible();
  await assertAccessible(page);

  await page.getByLabel(/I understand and want to delete/).check();
  await page.getByRole("button", { name: "Delete session" }).click();
  await expect(
    page.getByRole("heading", { name: "Session deleted" }),
  ).toBeVisible();
});

test("validation, recovery, keyboard focus, and mobile layout are usable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 760 });
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("button", { name: "Begin synthetic walkthrough" }),
  ).toBeFocused();
  await page
    .getByRole("button", { name: "Begin synthetic walkthrough" })
    .click();
  await page.getByLabel("Age range").selectOption("under_18");
  await page
    .getByLabel(/I understand this is a synthetic demonstration/)
    .check();
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "eligible age range" }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Leave" }).click();
  await page.getByRole("button", { name: "Recover a session" }).click();
  await page.getByLabel("Participant ID").fill("synthetic-returning-person");
  await page.getByLabel("Recovery code").fill("SYNTHETIC-DEMO");
  await page.getByRole("button", { name: "Recover", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Starting point" }),
  ).toBeVisible();
  await assertAccessible(page);
  const horizontalOverflow = await page.evaluate(
    () =>
      document.documentElement.scrollWidth >
      document.documentElement.clientWidth,
  );
  expect(horizontalOverflow).toBe(false);
});
