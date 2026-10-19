# Completed evaluation captures

[Second-Responder-Eval-Results.xlsx](Second-Responder-Eval-Results.xlsx) contains
nine manually scored responses on the `Eval Log` sheet, rows 7–15. Rows 7–13
are seven baseline runbook questions; rows 14–15 are the two prompt-v3 payments
retests. These are recorded development reviews, not fresh executions or an
automated benchmark. Claim counts and critical-error judgments retain their
original manual-review limitations.

## Capture repairs

When the user saved the completed workbook for submission, three capture gaps
were found. The following cells were restored from the user's earlier pasted
submissions in the development conversation:

| Cell | Gap | Restoration |
| --- | --- | --- |
| B7 | Baseline payments answer ended partway through its third first-check step | Full previously submitted answer, with readable line breaks and Markdown citations; the original erroneous remediation wording is preserved |
| C9 | SSO evidence was missing | Earlier Format Evidence JSON for the same question |
| C15 | Notes were pasted in the evidence column | Earlier Format Evidence JSON for the second v3 payments run; notes remain in H15 |

Evidence JSON was pretty-printed without changing its values. All other cell
values, including supported/total counts, notes, critical-error flags, formulas,
and their nine cached scores, were verified unchanged. Each of the nine evidence
questions matches its row's question. The workbook ZIP integrity check passed.
These checks validate capture integrity, not the underlying faithfulness grades.

An untouched original is retained locally in the ignored `raw/` directory.
It is not included in the public repository. SHA-256 hashes at review time:

```text
Original: 8bf983566c3199ca995927fa79e0661c30fbff28f9df7072520dac7977181a14
Reviewed: 6a6b7d59dea3f1b085fe41944f8a3bd956eb8c73dc170df6da870c8ba2fb3599
```

The unscored v2 retest appears only in
[manual-review-results.csv](../manual-review-results.csv). It is not a tenth
scored workbook row. Keep later executions in new rows and record the prompt
version in Notes.
