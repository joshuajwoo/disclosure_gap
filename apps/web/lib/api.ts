const API_URL = process.env.NEXT_PUBLIC_API_URL;

export class ApiClientError extends Error {
  constructor(
    message: string,
    readonly code: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  if (!API_URL) {
    throw new ApiClientError(
      "Live API access is not configured for this build.",
      "api_not_configured",
    );
  }
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  const body = (await response.json()) as
    T | { error?: { code?: string; message?: string } };
  if (!response.ok) {
    const error = (body as { error?: { code?: string; message?: string } })
      .error;
    throw new ApiClientError(
      error?.message ?? "The request could not be completed.",
      error?.code ?? "request_failed",
    );
  }
  return body as T;
}

export type Credentials = {
  participantId: string;
  sessionToken: string;
  recoveryCode?: string;
};

export async function enroll(ageBand: "18_19" | "20_22"): Promise<Credentials> {
  return request<Credentials>("/v1/participants", {
    method: "POST",
    body: JSON.stringify({
      contractVersion: "1.0.0-draft",
      ageBand,
      consentVersion: "0.2.0",
      consentAction: "agree",
    }),
  });
}

export async function recover(
  participantId: string,
  recoveryCode: string,
): Promise<Credentials> {
  const response = await request<{ sessionToken: string }>(
    "/v1/sessions/recover",
    {
      method: "POST",
      body: JSON.stringify({ participantId, recoveryCode }),
    },
  );
  return { participantId, sessionToken: response.sessionToken };
}

export async function submitAssessment(
  token: string,
  kind: "baseline" | "follow_up",
  responses: Array<number | "prefer_not_to_answer">,
): Promise<void> {
  await request("/v1/assessments", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify({
      contractVersion: "1.0.0-draft",
      assessmentType: kind,
      instrumentName: "apa_dsm5tr_sad_adult",
      instrumentVersion: "DSM-5-TR-2022",
      language: "en",
      responses: responses.map((responseCode, index) => ({
        itemCode: `SAD${String(index + 1).padStart(2, "0")}`,
        responseCode,
      })),
      completedAt: new Date().toISOString(),
    }),
  });
}

export async function submitBaselineContext(
  token: string,
  values: {
    supportConfidence: number | "no_person" | "prefer_not_to_answer";
    everydayComfort: number | "not_applicable" | "prefer_not_to_answer";
    insecurityComfort: number | "not_applicable" | "prefer_not_to_answer";
  },
): Promise<void> {
  await request("/v1/baseline-context", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify({
      contractVersion: "1.0.0-draft",
      ...values,
      completedAt: new Date().toISOString(),
    }),
  });
}

export async function submitCheckIn(
  token: string,
  payload: Record<string, unknown>,
): Promise<void> {
  await request("/v1/check-ins", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify(payload),
  });
}

export async function fetchTrends(
  token: string,
): Promise<Record<string, unknown>> {
  return request("/v1/me/trends", {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function deleteMe(token: string): Promise<void> {
  await request("/v1/me", {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}
