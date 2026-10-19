# Exported Code-node JavaScript

These files are extracted from reviewed workflow JSON and use n8n runtime
variables. They are node bodies, not standalone CLI applications.

| File | Workflow and node | Purpose |
| --- | --- | --- |
| `prepare-document.js` | Ingestion → Prepare Document | Decode GitHub base64 text and preserve metadata |
| `format-evidence.js` | Chat → Format Evidence | Combine retrieved documents with source IDs and the question |
| `render-cited-answer.js` | Chat → Render Cited Answer | Validate response shape/references and render GitHub citations |

Workflow JSON is authoritative. Regenerate copies with
`python3 scripts/prepare_workflows.py` when reviewed originals are available in
`workflows/raw/`. Tests compare these files with workflow parameters for drift.

Run local checks from the repository root with Node.js 20:

```sh
node --test tests/workflow-code.test.cjs
```

Mocks supply `$json`, `$input`, and named-node lookups. No API credentials or
network calls are used. A passing result does not verify model faithfulness or
prove successful import into a particular n8n application version.
