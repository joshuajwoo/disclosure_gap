"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import {
  ApiClientError,
  Credentials,
  deleteMe,
  enroll,
  fetchTrends,
  recover,
  submitAssessment,
  submitBaselineContext,
  submitCheckIn,
} from "../lib/api";

type Stage =
  | "welcome"
  | "recover"
  | "consent"
  | "baseline"
  | "check_in"
  | "follow_up"
  | "trends"
  | "deleted";
type InstrumentResponse = number | "prefer_not_to_answer";

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE !== "false";
const INSTRUMENT_SOURCE =
  "https://www.psychiatry.org/File%20Library/Psychiatrists/Practice/DSM/DSM-5-TR/APA-DSM5TR-SeverityMeasureForSocialAnxietyDisorderAdult.pdf";

function InstrumentFields({
  legend,
  values,
  onChange,
}: {
  legend: string;
  values: InstrumentResponse[];
  onChange: (index: number, value: InstrumentResponse) => void;
}) {
  return (
    <fieldset>
      <legend>{legend}</legend>
      <p className="hint">
        The public synthetic demo identifies the ten official items by code
        without reproducing their wording. Review the{" "}
        <a href={INSTRUMENT_SOURCE} target="_blank" rel="noreferrer">
          official APA form
        </a>{" "}
        alongside this response grid. No score or diagnostic label is shown.
      </p>
      <div className="instrument-grid">
        {values.map((value, index) => {
          const code = `SAD${String(index + 1).padStart(2, "0")}`;
          return (
            <div className="field" key={code}>
              <label htmlFor={`${legend}-${code}`}>{code} response</label>
              <select
                id={`${legend}-${code}`}
                value={value}
                onChange={(event) =>
                  onChange(
                    index,
                    event.target.value === "prefer_not_to_answer"
                      ? "prefer_not_to_answer"
                      : Number(event.target.value),
                  )
                }
              >
                {[0, 1, 2, 3, 4].map((option) => (
                  <option value={option} key={option}>
                    {option}
                  </option>
                ))}
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
          );
        })}
      </div>
    </fieldset>
  );
}

export function StudyExperience() {
  const [stage, setStage] = useState<Stage>("welcome");
  const [ageBand, setAgeBand] = useState("");
  const [consented, setConsented] = useState(false);
  const [credentials, setCredentials] = useState<Credentials | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [week, setWeek] = useState(1);
  const [completedCheckIns, setCompletedCheckIns] = useState(0);
  const [eligibleWeeks, setEligibleWeeks] = useState(0);
  const [sharedWeeks, setSharedWeeks] = useState(0);
  const [keptPrivateWeeks, setKeptPrivateWeeks] = useState(0);
  const [baselineResponses, setBaselineResponses] = useState<
    InstrumentResponse[]
  >(Array(10).fill(0));
  const [followUpResponses, setFollowUpResponses] = useState<
    InstrumentResponse[]
  >(Array(10).fill(0));
  const [baselineSupport, setBaselineSupport] = useState("3");
  const [everydayComfort, setEverydayComfort] = useState("3");
  const [insecurityComfort, setInsecurityComfort] = useState("3");
  const [wantedToShare, setWantedToShare] = useState("yes");
  const [sharingAction, setSharingAction] = useState("shared");
  const [audience, setAudience] = useState("friend");
  const [expectedComfort, setExpectedComfort] = useState("3");
  const [anticipatedJudgment, setAnticipatedJudgment] = useState("no");
  const [supportConfidence, setSupportConfidence] = useState("3");
  const [concernCategory, setConcernCategory] = useState("everyday");
  const [recoveryParticipantId, setRecoveryParticipantId] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");
  const [confirmDeletion, setConfirmDeletion] = useState(false);
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus();
  }, [stage]);

  useEffect(() => {
    if (!DEMO_MODE) {
      const stored = sessionStorage.getItem("disclosure-gap-session");
      if (stored) setCredentials(JSON.parse(stored) as Credentials);
    }
  }, []);

  const progress = useMemo(() => {
    const labels: Record<Stage, string> = {
      welcome: "Introduction",
      recover: "Recovery",
      consent: "Eligibility and consent",
      baseline: "Baseline",
      check_in: `Weekly check-in ${week} of 4`,
      follow_up: "Follow-up",
      trends: "Your descriptive summary",
      deleted: "Session deleted",
    };
    return labels[stage];
  }, [stage, week]);

  function showError(problem: unknown) {
    setError(
      problem instanceof ApiClientError
        ? problem.message
        : "Something went wrong. Your answers were not submitted.",
    );
  }

  async function start(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!consented || !["18_19", "20_22"].includes(ageBand)) {
      setError(
        "Confirm an eligible age range and consent to continue, or leave the walkthrough.",
      );
      return;
    }
    setBusy(true);
    try {
      const result = DEMO_MODE
        ? {
            participantId: "synthetic-demo-participant",
            sessionToken: "synthetic-demo-session",
            recoveryCode: "SYNTHETIC-DEMO",
          }
        : await enroll(ageBand as "18_19" | "20_22");
      setCredentials(result);
      if (!DEMO_MODE)
        sessionStorage.setItem(
          "disclosure-gap-session",
          JSON.stringify(result),
        );
      setStage("baseline");
    } catch (problem) {
      showError(problem);
    } finally {
      setBusy(false);
    }
  }

  async function recoverSession(event: FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const result = DEMO_MODE
        ? recoveryCode === "SYNTHETIC-DEMO"
          ? {
              participantId:
                recoveryParticipantId || "synthetic-demo-participant",
              sessionToken: "synthetic-demo-session",
            }
          : null
        : await recover(recoveryParticipantId, recoveryCode);
      if (!result)
        throw new ApiClientError(
          "The synthetic recovery information was not accepted.",
          "recovery_failed",
        );
      setCredentials(result);
      if (!DEMO_MODE)
        sessionStorage.setItem(
          "disclosure-gap-session",
          JSON.stringify(result),
        );
      setStage("baseline");
    } catch (problem) {
      showError(problem);
    } finally {
      setBusy(false);
    }
  }

  async function saveAssessment(
    kind: "baseline" | "follow_up",
    values: InstrumentResponse[],
  ) {
    setError("");
    if (!credentials) return;
    setBusy(true);
    try {
      if (!DEMO_MODE) {
        if (kind === "baseline") {
          const ordinal = (value: string) =>
            ["no_person", "not_applicable", "prefer_not_to_answer"].includes(
              value,
            )
              ? value
              : Number(value);
          await submitBaselineContext(credentials.sessionToken, {
            supportConfidence: ordinal(baselineSupport) as
              number | "no_person" | "prefer_not_to_answer",
            everydayComfort: ordinal(everydayComfort) as
              number | "not_applicable" | "prefer_not_to_answer",
            insecurityComfort: ordinal(insecurityComfort) as
              number | "not_applicable" | "prefer_not_to_answer",
          });
        }
        await submitAssessment(credentials.sessionToken, kind, values);
      }
      setStage(kind === "baseline" ? "check_in" : "trends");
      if (kind === "follow_up" && !DEMO_MODE) {
        const trends = await fetchTrends(credentials.sessionToken);
        setCompletedCheckIns(Number(trends.completedCheckIns ?? 0));
        setEligibleWeeks(Number(trends.eligibleWantedWeeks ?? 0));
        setSharedWeeks(Number(trends.sharedWeeks ?? 0));
        setKeptPrivateWeeks(Number(trends.keptPrivateWeeks ?? 0));
      }
    } catch (problem) {
      showError(problem);
    } finally {
      setBusy(false);
    }
  }

  async function saveCheckIn(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!credentials) return;
    const wanted = wantedToShare === "yes";
    const payload: Record<string, unknown> = {
      contractVersion: "1.0.0-draft",
      week,
      wantedToShare,
      completedAt: new Date().toISOString(),
    };
    if (wanted) {
      Object.assign(payload, {
        intendedAudience: audience,
        sharingAction,
        expectedComfort:
          expectedComfort === "prefer_not_to_answer"
            ? expectedComfort
            : Number(expectedComfort),
        anticipatedJudgment,
        supportConfidence:
          supportConfidence === "prefer_not_to_answer"
            ? supportConfidence
            : Number(supportConfidence),
        concernCategory,
      });
    }
    setBusy(true);
    try {
      if (!DEMO_MODE) await submitCheckIn(credentials.sessionToken, payload);
      setCompletedCheckIns((value) => value + 1);
      if (wanted) {
        setEligibleWeeks((value) => value + 1);
        if (sharingAction === "shared") setSharedWeeks((value) => value + 1);
        if (sharingAction === "chose_private")
          setKeptPrivateWeeks((value) => value + 1);
      }
      if (week < 4) setWeek((value) => value + 1);
      else setStage("follow_up");
    } catch (problem) {
      showError(problem);
    } finally {
      setBusy(false);
    }
  }

  async function removeSession() {
    if (!credentials || !confirmDeletion) return;
    setBusy(true);
    setError("");
    try {
      if (!DEMO_MODE) await deleteMe(credentials.sessionToken);
      sessionStorage.removeItem("disclosure-gap-session");
      localStorage.removeItem("disclosure-gap-demo");
      setCredentials(null);
      setStage("deleted");
    } catch (problem) {
      showError(problem);
    } finally {
      setBusy(false);
    }
  }

  const responseForm = (
    label: string,
    values: InstrumentResponse[],
    setter: React.Dispatch<React.SetStateAction<InstrumentResponse[]>>,
    kind: "baseline" | "follow_up",
  ) => (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void saveAssessment(kind, values);
      }}
    >
      <InstrumentFields
        legend={label}
        values={values}
        onChange={(index, value) =>
          setter((current) =>
            current.map((entry, item) => (item === index ? value : entry)),
          )
        }
      />
      <button className="button" disabled={busy} type="submit">
        {kind === "baseline" ? "Save baseline" : "Complete follow-up"}
      </button>
    </form>
  );

  return (
    <main className="shell">
      <div className="banner" role="status" data-testid="synthetic-banner">
        <span aria-hidden="true">◆</span>
        SYNTHETIC DEMO — no real participant data is collected here
      </div>

      {stage === "welcome" && (
        <section className="hero">
          <p className="eyebrow">A privacy-first engineering case study</p>
          <h1 ref={headingRef} tabIndex={-1}>
            What we choose to share—and what we keep.
          </h1>
          <p className="lede">
            Explore a fictional four-week study flow built to demonstrate
            careful contracts, missingness, privacy choices, and deletion.
            Choosing privacy can be healthy. This demo does not diagnose or
            predict anyone.
          </p>
          <div className="actions">
            <button className="button" onClick={() => setStage("consent")}>
              Begin synthetic walkthrough
            </button>
            <button
              className="button secondary"
              onClick={() => setStage("recover")}
            >
              Recover a session
            </button>
          </div>
        </section>
      )}

      {stage !== "welcome" && (
        <p className="progress" aria-live="polite">
          {progress}
        </p>
      )}
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {stage === "consent" && (
        <section className="card">
          <p className="eyebrow">Step 1</p>
          <h1 ref={headingRef} tabIndex={-1}>
            Eligibility and consent
          </h1>
          <p>
            This synthetic walkthrough mirrors a proposed adult study. It asks
            structured questions only—never names, contacts, locations, or the
            content of a concern.
          </p>
          <form onSubmit={(event) => void start(event)} noValidate>
            <div className="field">
              <label htmlFor="age-band">Age range</label>
              <select
                id="age-band"
                value={ageBand}
                onChange={(event) => setAgeBand(event.target.value)}
              >
                <option value="">Choose an option</option>
                <option value="under_18">Under 18</option>
                <option value="18_19">18–19</option>
                <option value="20_22">20–22</option>
                <option value="23_or_older">23 or older</option>
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
            <label className="check-row">
              <input
                type="checkbox"
                checked={consented}
                onChange={(event) => setConsented(event.target.checked)}
              />
              <span>
                I understand this is a synthetic demonstration and agree to
                continue through the fictional flow.
              </span>
            </label>
            <div className="actions">
              <button className="button" disabled={busy} type="submit">
                Continue
              </button>
              <button
                className="button secondary"
                type="button"
                onClick={() => setStage("welcome")}
              >
                Leave
              </button>
            </div>
          </form>
        </section>
      )}

      {stage === "recover" && (
        <section className="card">
          <h1 ref={headingRef} tabIndex={-1}>
            Recover a session
          </h1>
          <p>
            A recovery code is the key to a session. Keep it private; the
            service cannot email or look it up for you. For this demo, use{" "}
            <strong>SYNTHETIC-DEMO</strong>.
          </p>
          <form onSubmit={(event) => void recoverSession(event)}>
            <div className="field">
              <label htmlFor="participant-id">Participant ID</label>
              <input
                id="participant-id"
                type="text"
                value={recoveryParticipantId}
                onChange={(event) =>
                  setRecoveryParticipantId(event.target.value)
                }
              />
            </div>
            <div className="field">
              <label htmlFor="recovery-code">Recovery code</label>
              <input
                id="recovery-code"
                type="text"
                value={recoveryCode}
                onChange={(event) => setRecoveryCode(event.target.value)}
              />
            </div>
            <div className="actions">
              <button className="button" disabled={busy} type="submit">
                Recover
              </button>
              <button
                className="button secondary"
                type="button"
                onClick={() => setStage("welcome")}
              >
                Back
              </button>
            </div>
          </form>
        </section>
      )}

      {stage === "baseline" && (
        <section className="card">
          <p className="eyebrow">Synthetic baseline</p>
          <h1 ref={headingRef} tabIndex={-1}>
            Starting point
          </h1>
          {credentials?.recoveryCode && (
            <p className="summary">
              Demo recovery code: <strong>{credentials.recoveryCode}</strong>. A
              real code would be shown once and stored only as a strong hash.
            </p>
          )}
          <div className="grid">
            <div className="field">
              <label htmlFor="baseline-support">
                Confidence in supportive response
              </label>
              <select
                id="baseline-support"
                value={baselineSupport}
                onChange={(event) => setBaselineSupport(event.target.value)}
              >
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value}>{value}</option>
                ))}
                <option value="no_person">No person in mind</option>
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="everyday-comfort">
                Comfort discussing everyday problems
              </label>
              <select
                id="everyday-comfort"
                value={everydayComfort}
                onChange={(event) => setEverydayComfort(event.target.value)}
              >
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value}>{value}</option>
                ))}
                <option value="not_applicable">Not applicable</option>
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="insecurity-comfort">
                Comfort discussing a personal insecurity
              </label>
              <select
                id="insecurity-comfort"
                value={insecurityComfort}
                onChange={(event) => setInsecurityComfort(event.target.value)}
              >
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value}>{value}</option>
                ))}
                <option value="not_applicable">Not applicable</option>
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
          </div>
          {responseForm(
            "Baseline instrument",
            baselineResponses,
            setBaselineResponses,
            "baseline",
          )}
        </section>
      )}

      {stage === "check_in" && (
        <section className="card">
          <p className="eyebrow">Week {week}</p>
          <h1 ref={headingRef} tabIndex={-1}>
            A short check-in
          </h1>
          <p>
            Choosing whether to share is personal. Keeping something private can
            be healthy.
          </p>
          <form onSubmit={(event) => void saveCheckIn(event)}>
            <div className="field">
              <label htmlFor="wanted-to-share">
                Did you want to talk about a personal concern?
              </label>
              <select
                id="wanted-to-share"
                value={wantedToShare}
                onChange={(event) => setWantedToShare(event.target.value)}
              >
                <option value="yes">Yes</option>
                <option value="no">No</option>
                <option value="not_sure">Not sure</option>
                <option value="prefer_not_to_answer">
                  Prefer not to answer
                </option>
              </select>
            </div>
            {wantedToShare === "yes" && (
              <div className="grid" data-testid="check-in-followups">
                <div className="field">
                  <label htmlFor="audience">Person you had in mind</label>
                  <select
                    id="audience"
                    value={audience}
                    onChange={(event) => setAudience(event.target.value)}
                  >
                    <option value="friend">Friend</option>
                    <option value="family">Family</option>
                    <option value="partner">Partner</option>
                    <option value="other_trusted">Other trusted person</option>
                    <option value="no_particular_person">
                      No particular person
                    </option>
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="sharing-action">What happened?</label>
                  <select
                    id="sharing-action"
                    value={sharingAction}
                    onChange={(event) => setSharingAction(event.target.value)}
                  >
                    <option value="shared">I shared</option>
                    <option value="not_shared">I did not share</option>
                    <option value="chose_private">
                      I chose to keep it private
                    </option>
                    <option value="no_safe_opportunity">
                      There was no safe opportunity
                    </option>
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="expected-comfort">Expected comfort</label>
                  <select
                    id="expected-comfort"
                    value={expectedComfort}
                    onChange={(event) => setExpectedComfort(event.target.value)}
                  >
                    {[1, 2, 3, 4, 5].map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="anticipated-judgment">
                    Did you anticipate judgment?
                  </label>
                  <select
                    id="anticipated-judgment"
                    value={anticipatedJudgment}
                    onChange={(event) =>
                      setAnticipatedJudgment(event.target.value)
                    }
                  >
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                    <option value="shared_as_wanted">Shared as wanted</option>
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="support-confidence">
                    Confidence in support
                  </label>
                  <select
                    id="support-confidence"
                    value={supportConfidence}
                    onChange={(event) =>
                      setSupportConfidence(event.target.value)
                    }
                  >
                    {[1, 2, 3, 4, 5].map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="concern-category">Concern category</label>
                  <select
                    id="concern-category"
                    value={concernCategory}
                    onChange={(event) => setConcernCategory(event.target.value)}
                  >
                    <option value="everyday">Everyday</option>
                    <option value="personal_insecurity">
                      Personal insecurity
                    </option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_answer">
                      Prefer not to answer
                    </option>
                  </select>
                </div>
              </div>
            )}
            <button className="button" disabled={busy} type="submit">
              Save week {week}
            </button>
          </form>
        </section>
      )}

      {stage === "follow_up" && (
        <section className="card">
          <p className="eyebrow">Synthetic follow-up</p>
          <h1 ref={headingRef} tabIndex={-1}>
            Four-week follow-up
          </h1>
          {responseForm(
            "Follow-up instrument",
            followUpResponses,
            setFollowUpResponses,
            "follow_up",
          )}
        </section>
      )}

      {stage === "trends" && (
        <section className="card">
          <p className="eyebrow">Descriptive only</p>
          <h1 ref={headingRef} tabIndex={-1}>
            Your fictional summary
          </h1>
          <p className="summary" data-testid="trend-summary">
            {eligibleWeeks
              ? `In ${sharedWeeks} of ${eligibleWeeks} check-ins where you wanted to talk with someone, you reported talking with them.`
              : "There is not enough information to summarize this pattern."}
          </p>
          <p>
            Completed check-ins: {completedCheckIns}. Chose privacy:{" "}
            {keptPrivateWeeks}. These counts describe only the fictional answers
            entered here. They are not a diagnosis, risk estimate,
            recommendation, or comparison with other people.
          </p>
          <fieldset>
            <legend>Delete this session</legend>
            <p className="hint">
              Deletion removes submitted responses and invalidates session and
              recovery credentials under the documented policy.
            </p>
            <label className="check-row">
              <input
                type="checkbox"
                checked={confirmDeletion}
                onChange={(event) => setConfirmDeletion(event.target.checked)}
              />
              <span>
                I understand and want to delete this synthetic session.
              </span>
            </label>
            <button
              className="button danger"
              type="button"
              disabled={!confirmDeletion || busy}
              onClick={() => void removeSession()}
            >
              Delete session
            </button>
          </fieldset>
        </section>
      )}

      {stage === "deleted" && (
        <section className="card">
          <h1 ref={headingRef} tabIndex={-1}>
            Session deleted
          </h1>
          <p>
            The synthetic responses and access credentials are no longer
            available in this session.
          </p>
          <button className="button" onClick={() => window.location.reload()}>
            Return to introduction
          </button>
        </section>
      )}
    </main>
  );
}
