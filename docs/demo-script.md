# Second Responder demo script

Target recording length: **about 2:40**, with a hard submission limit below
3:00. Speak only the quoted narration; screen directions and timestamps are
not narration. The spoken script is deliberately short to leave room for clicks
and the model response. Rehearse once with actual response latency.

## Before recording

- Open the repository, all three n8n workflows, the chat panel, and the actual
  saved evaluation workbook or `evaluation/manual-review-results.csv`.
- Use the editor chat or a verified published chat workflow containing Prompt v3.
- Use only synthetic runbook data. Hide credential/settings screens and unrelated tabs.
- Keep the payments question ready to paste.
- Confirm the GitHub repository shows the final commit containing all three
  reviewed workflow exports before recording.
- If the live answer is incorrect, describe what happened honestly. Do not
  present an earlier successful answer as the new execution.

## 0:00–0:18 — Problem and project

**Screen:** GitHub repository overview.

> “This is Second Responder, an n8n RAG prototype for on-call engineers. It answers
> ‘What should I do for this alert?’ using twelve synthetic service runbooks,
> and links its instructions back to the source.”

## 0:18–0:43 — Architecture

**Screen:** Briefly show ingestion, retrieval, and chat canvases; keep zoom readable.

> “There are three workflows. Ingestion reads GitHub markdown, creates OpenAI
> embeddings, and stores documents in Pinecone. Retrieval accepts a question and
> returns the top three matches. The chat workflow formats that evidence, uses a
> Basic LLM Chain with structured output, and renders clickable citations.”

## 0:43–1:30 — Live question and cited response

**Screen:** Chat. Paste and submit:

```text
What should I check when payments-api /charge returns 5xx errors and Stripe requests time out?
```

**While it runs, say:**

> “I’ll ask about payments errors and Stripe timeouts. Retrieval is mandatory
> before generation. The answer should preserve commands, remediation
> prerequisites, and escalation thresholds from the retrieved text.”

**Once the answer appears:** show the first checks, the conditional RB-009 step,
and click a runbook citation if time permits.

> “Here are the checks and conditional actions, with source links. The key detail
> is that following RB-009 requires connection-pool saturation. A possible pool
> problem alone should not authorize that remediation.”

If that condition is wrong in the live answer, replace the preceding paragraph
with: “This run broadened the prerequisite. I would flag it as a critical error;
a citation link alone does not establish support.”

## 1:30–2:10 — Evaluation and prompt experiment

**Screen:** Evaluation record. Point to the initial payments row and the two v3 rows.

> “I evaluate individual claims against the evidence from the same execution.
> Faithfulness is supported claims divided by total claims, with critical errors
> tracked separately. The initial payments answer scored ninety-four percent
> but still broadened a remediation condition. Prompt version three made the
> source-action prerequisite explicit. Two reviewed runs retained it, scoring
> one hundred percent and ninety-two percent, with no critical errors identified.”

## 2:10–2:40 — Boundaries and repository artifacts

**Screen:** `PROJECT.md`, then the final `workflows/` folder.

> “These are development results, not proof of ninety-percent performance on
> unseen incidents. Next I’ll expand testing and calibrate automated grading.
> Runbook text reaches both embedding and chat APIs, so sensitive deployments
> need data controls before those calls. The repository contains the workflow
> exports, prompts, runbooks, evaluation tooling, and detailed project report.”

## Timing and final check

- Keep the finished video below three minutes; aim to stop around 2:40.
- If the workflow is slow, shorten canvas tours and source-link navigation rather
  than adding unplanned explanation. Rehearse again if the recording exceeds the limit.
- Pause between the two evaluation scores so they are clearly **100% and 92%**.
- Add the final Loom URL to `PROJECT.md`. Review the shared video for accidental
  exposure of credentials or nonsynthetic information before submission.
