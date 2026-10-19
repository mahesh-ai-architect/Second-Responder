# Development findings and limitations

## Problem and approach

The prototype answers on-call alert questions from 12 synthetic markdown
runbooks. Retrieval is mandatory before the answer step. OpenAI embeddings
support similarity search in Pinecone; n8n formats retrieved evidence for a
Basic LLM Chain and renders source IDs as GitHub citations.

## A working citation can still support an incorrect instruction

The payments answer linked to RB-001 but expanded an action's prerequisite:

- Source diagnosis: “no healthy upstream” can indicate connection-pool or target-pod problems.
- Source action: follow RB-009 for pool saturation.
- Initial answer: follow RB-009 for the symptom or suspected pool/target-pod issues.

The source URL was valid. The action's trigger was not preserved. Manual review
counted 16 of 17 claims as supported (94%) and still marked a critical error.
This motivated tracking critical operational errors separately from the mean.

## Prompt experiment

The prompt with an appended prerequisite rule and example still produced the
broadened trigger in one retest. The complete text is in `prompts/system-v2.txt`.

Prompt v3 consolidated the instructions, required remediation to be constructed
from the source action instruction, kept diagnostic possibilities separate,
preserved prerequisites, and requested a final source check. It also clarified
section labels, alternatives, and recovery criteria. The output schema stayed
the same.

Two reviewed v3 runs preserved the pool-saturation prerequisite:

| Run | Supported / total | Critical error | Observation |
| --- | --- | --- | --- |
| v3 run 1 | 14 / 14 (100%) | No | Required condition retained |
| v3 run 2 | 12 / 13 (92%) | No | Condition retained; deploy-feed check gained an unsupported prerequisite under the conservative rubric |

The prompts changed in several ways, so these results do not identify which
individual instruction caused the improvement. The prompt contains a payments
example from this evaluation case. These are development tests, not held-out
evidence of generalization. The model's requested self-check is not an
independent verifier.

## Evaluation boundaries

- Reviews were manual and performed in the development conversation.
- Claim decomposition and strict support judgments require reviewer calibration.
- Some recovery and “alternative” wording was marked unsupported conservatively.
- A faithful response may still be incomplete or reproduce an incorrect runbook.
- The citation renderer checks references and URLs, not factual support.
- No calibrated automated grader, reserved test set, or statistically established production faithfulness result is available.
- Seven of the twelve runbooks received baseline question reviews; remaining cases and ambiguity/unsupported cases still need testing.
- All three exports were imported as copies in n8n Cloud 2.43.7. The chat export confirms `gpt-5-mini`. Selecting **When Last Node Finishes** resolved chat delivery. The ingestion copy populated a new namespace with 12 records; retrieval execution 56 confirms three documents were returned from that namespace, and the imported chat displayed the answer. This functional check does not assign a new faithfulness score.

## Privacy boundaries

In this design, runbook text goes to OpenAI during ingestion embedding; the
engineer's question goes to query embedding; the question and retrieved text go
to the chat model. Vectorization does not prevent this processing. Pinecone,
saved n8n executions, GitHub, and evaluation files can also hold document text.

Redaction must happen before the relevant external call if sensitive information
must be withheld. A system instruction not to reveal PII does not stop input
data from reaching the provider. Retention/training policies and account
controls are separate considerations; account-specific settings were not
audited. Only synthetic material is intended for the public assignment repo.

## Next work

1. Finish GitHub packaging and the Loom recording. All three imports and retrieval
   from the new ingestion namespace have been checked. The saved scoring workbook
   includes all nine scored responses and their evidence, with capture repairs documented.
2. Repeat the payments case again without changing v3; check for reappearing critical errors.
3. Run the other development cases against v3 to detect regressions.
4. Add unseen cases for conditional thresholds, cross-runbook retrieval, ambiguity, and unsupported questions.
5. Calibrate an automated claim-support grader with engineer-reviewed labels.
6. Add session-aware history and evaluate follow-up questions if conversational context is required.
