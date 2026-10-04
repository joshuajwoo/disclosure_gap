import { readFileSync } from "node:fs";
import { test, expect } from "@playwright/test";

test("default configuration prevents real participant data", () => {
  const environment = readFileSync(".env.example", "utf8");
  expect(environment).toContain("APP_ENV=local-synthetic");
  expect(environment).toContain("ALLOW_REAL_PARTICIPANT_DATA=false");
});

test("draft contract records the selected outcome and normative source", () => {
  const manifest = JSON.parse(
    readFileSync("packages/contracts/v1/manifest.json", "utf8"),
  ) as {
    status: string;
    outcomeInstrument: {
      status: string;
      name: string;
      version: string;
      itemsIncluded: boolean;
      wordingSource: string;
    };
  };

  expect(manifest.status).toBe("synthetic-only");
  expect(manifest.outcomeInstrument).toEqual({
    status: "selected-research-reproduction-permitted",
    name: "apa_dsm5tr_sad_adult",
    version: "DSM-5-TR-2022",
    itemsIncluded: false,
    wordingSource: "official-normative-pdf",
  });
});
