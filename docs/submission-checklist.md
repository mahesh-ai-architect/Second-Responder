# Submission checklist

## Required project files

- [x] Twelve synthetic markdown runbooks and corpus README.
- [x] Project README describing the problem, architecture, and current status.
- [x] Detailed Markdown project report: `PROJECT.md`.
- [x] Demo narrative and screen sequence targeted below three minutes: `docs/demo-script.md`.
- [x] Setup instructions with index, embedding, namespace, and workflow-link configuration.
- [x] Prompt v2 and v3 snapshots.
- [x] Spreadsheet templates and their generator code.
- [x] Manual result summary with provenance and limitations.
- [x] Actual reviewed ingestion export: `workflows/01-ingestion.json`.
- [x] Actual reviewed retrieval export: `workflows/02-retrieval.json`.
- [x] Actual reviewed chat export: `workflows/03-chat.json`.
- [x] Chat model `gpt-5-mini` and empty serialized model options recorded.
- [x] Code-node JavaScript extracted and checked against reviewed exports.
- [x] n8n Cloud, application version 2.43.7, recorded from the About n8n screenshot.
- [x] Filled workbook saved in `evaluation/results/Second-Responder-Eval-Results.xlsx`; nine scores and evidence captures checked.
- [ ] Screenshots/demo evidence added if required by the rubric.
- [ ] Loom demo recorded below three minutes and its link added to `PROJECT.md`.
- [ ] Final GitHub repository link, Loom link, and detailed Markdown document ready for submission.

The checklist is a snapshot; update it when the pending artifacts are actually
present and verified. Local changes are not on GitHub until committed and pushed.

## Export review and reproduction

- [x] JSON files parse and include all attached sub-nodes and embedded Code-node logic.
- [x] Exports reviewed; credential bindings, instance metadata, and pinned data excluded from public copies.
- [x] Chat export contains the tested prompt version and citation renderer.
- [x] Retrieval namespace matches the observed development namespace with no surrounding whitespace.
- [x] Original chat-to-retrieval reference and query input contract verified; all 13 local checks passed.
- [x] Imported chat copy targets the imported retrieval copy by ID; query mapping executed successfully.
- [x] Chat and retrieval imports tested as copies in the existing Cloud instance; existing credentials selected.
- [x] Chat response mode explicitly set to When Last Node Finishes; user confirmed the answer appears in chat.
- [x] Ingestion export imported as a separate copy; a new execution populated `second-responder-runbooks-52` with 12 records.
- [x] Imported chat/retrieval copies tested against `second-responder-runbooks-52`; retrieval execution 56 (parent 55) confirms the namespace and three returned documents.
- [x] Imported chat/retrieval copies produce retrieved items, a structured answer, and a rendered response with citations using the existing namespace.
- [ ] Claims in that test are compared with its actual retrieved evidence.

## Git review and submission

From the `Second Responder` repository directory:

```sh
git status --short
git diff --check
git diff --stat
```

Review new/untracked files as well; `git diff` does not show their contents.
After the exports and saved results are reviewed, stage the intended paths,
inspect the staged diff, then commit and push to the existing `origin/main`.
Do not commit `workflows/raw/`, `.env` files, or credentials backups.

Example commands to use **after** completing that review:

```sh
git add README.md PROJECT.md .gitignore requirements.txt docs prompts workflows evaluation code scripts tests
git diff --cached --check
git diff --cached --stat
git commit -m "Document Second Responder RAG workflows and evaluation"
git push origin main
```

Open the GitHub repository afterwards and verify that the final commit contains
all three JSON exports, code, prompts, saved results, and documentation. Confirm
the repository visibility matches the assignment instructions.
