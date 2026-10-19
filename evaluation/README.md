# Manual evaluation

Start with `Second-Responder-Simple-Eval.xlsx`: one sheet, one row per generated
answer. Its fields are question, answer, retrieved evidence, supported claims,
total claims, calculated faithfulness, critical error, and notes.

The larger workbook is an optional detailed template. The two workbooks directly
in this directory are blank templates. The [completed results](results/Second-Responder-Eval-Results.xlsx)
contain nine manually scored responses, saved answers, and retrieved evidence.
See the [capture review](results/README.md) for restored cells and provenance.

## Save the completed workbook

Save future filled copies in `evaluation/results/`. Retain the original response and evidence
when retesting; use a new row for each execution and identify the prompt version
in Notes. Inspect results for nonsynthetic material before publishing.

## Method

1. Capture the exact question and rendered answer from the same execution.
2. Save Format Evidence output, including retrieved text and source IDs.
3. Decompose the answer into checkable factual assertions and operational
   instructions. Keep an action's conditions attached to it. In these reviews,
   repeated advice was counted where it appeared in different sections.
4. Mark each claim supported or unsupported against that saved context.
5. Calculate `supported / total`. Zero-claim answers are N/A, not automatically
   100%; assess whether clarification or abstention was appropriate separately.
6. Track critical errors independently: unsupported commands, remediation
   prerequisites, and escalation thresholds. A high mean does not override one.
7. Record clarity/completeness issues and conservative judgments in Notes.

An early review found 16/17 claims supported but still identified a critical
condition error. The percent is not a confidence estimate or probability that
the answer is safe. A model-generated claim list/score was not used as a
calibrated grader in these experiments.

## Result provenance

`manual-review-results.csv` transcribes the numerical judgments made in the
development conversation. It is a compact review summary, not an automated
benchmark output or a replacement for the saved per-execution evidence. The
initial prompt text for every baseline run was not separately archived, so those
rows are labeled `baseline-before-v3` rather than asserting an exact v1 snapshot.
The v2 retest remained critically incorrect but was not fully claim-scored.

Seven baseline runbook questions and two v3 payments runs have numerical reviews.
Runbooks RB-008 through RB-012, a held-out set, and broader edge cases remain
untested in this record. Do not combine prompt versions into a reported v3 score.
Keep the scoring rubric fixed and calibrate reviewer judgments before scaling.

## Spreadsheet generation

`create_simple_eval.py` and `create_scoring_workbook.py` use Python 3 and
`XlsxWriter`. `requirements.txt` in the repository root lists that dependency.
The scripts recreate their named templates; keep completed results in the
separate `results/` directory and retain a copy before regeneration.

References:
- [Ragas faithfulness definition](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
