# Setup and reproduction

## Record the running environment

The observed environment is **n8n Cloud, version 2.43.7**, confirmed by the
user's About n8n screenshot during submission preparation. Cloud may update
after this observation; record your own version when reproducing the project.
The inspected chat export selects `gpt-5-mini` with empty model options and its
System message matches v3 after whitespace normalization. Node type versions
are not the n8n application version. Also record the source corpus version.

## Accounts and credentials

- GitHub access to the synthetic runbook repository.
- An OpenAI API credential in n8n for embeddings and the chat model.
- A Pinecone credential in n8n for the index.

Set credentials through n8n's credential interface. Repository JSON should not
include literal secret values. Importing a workflow does not provision external
accounts, recreate credentials, or restore Pinecone records.

## 1. Import and configure ingestion

Import the reviewed `workflows/01-ingestion.json`. The manually
built flow lists GitHub runbooks, keeps files starting `RB-` and ending `.md`,
fetches each file, and decodes its base64 content into document text.

Development settings:

- Source: `mahesh-ai-architect/Second-Responder`, branch `main`, directory `runbooks`.
- Filter: `type = file`, filename starts with `RB-`, filename ends with `.md`.
- Loop batch size: 1; the Pinecone insert output returns to the loop input.
- OpenAI embedding model: `text-embedding-3-small`, dimensions 1536.
- Pinecone index: `second-responder`, dense vectors, 1536 dimensions, cosine.
- Default Data Loader: JSON, Load Specific Data, text `{{ $json.text }}`.
- Metadata: filename, GitHub source URL, repository path, and file blob SHA.
- Recursive Character Text Splitter: chunk size 2000 characters, overlap 200.
- Clear Namespace: off.

The manual ingestion used a namespace expression:
`{{ 'second-responder-runbooks-' + $execution.id }}`.
The observed successful run populated `second-responder-runbooks-9` with 12
records. A new execution may create a different namespace. Record the namespace
actually written and configure retrieval to use it exactly, without surrounding
spaces. Do not assume this old snapshot exists in another Pinecone project.

The metadata `git_sha` is a **file blob SHA**, not a commit SHA. The source links
point to `main`; retain retrieved text with evaluation records so later changes
to `main` do not change the evidence used for an old score.

## 2. Configure retrieval

Import the reviewed `workflows/02-retrieval.json`.

1. In **When Executed by Another Workflow**, define `query` as a String input.
2. Set Pinecone mode to **Get Many**.
3. Set Prompt to expression `{{ $json.query }}`.
4. Select the index and exact populated namespace.
5. Set Limit to 3 and Include Metadata on.
6. Attach Embeddings OpenAI using the same embedding model/dimensions as ingestion.

Expected items contain `document.pageContent`, `document.metadata`, and `score`.
Similarity scores are retrieval signals, not faithfulness or correctness scores.

## 3. Configure the chat workflow

Import the reviewed `workflows/03-chat.json` after importing retrieval.

1. Reconnect the OpenAI chat credential and record the selected model.
2. In Execute Sub-workflow, select the imported retrieval workflow. Map its
   `query` input to `{{ $json.chatInput }}` and wait for completion.
   If the imported copy is absent from the list, select it by ID: open the copy
   and use the ID after `/workflow/` in its URL. Confirm the target is the copy.
3. Confirm Format Evidence is a JavaScript Code node running once for all items.
   It produces `question`, `context`, `sources`, and `sessionId`.
4. Confirm Basic LLM Chain takes its user prompt through **Define below**:

   ```text
   {{ 'Engineer question:\n' + $json.question + '\n\nRetrieved runbook evidence:\n' + $json.context }}
   ```

5. Use the System message in `prompts/system-v3.txt` for the current development
   retest. Verify it matches the exported node before submission.
6. Attach the OpenAI Chat Model and Structured Output Parser.
7. The parser's fields are `status`, `steps`, and `clarifying_question`; each step
   contains `section`, `text`, and `source_ids`.
8. Render Cited Answer maps source IDs to retrieved GitHub URLs and returns a
   string in `output`. It checks references, not semantic entailment.
9. Set Chat Trigger response mode to **When Last Node Finishes**.
   This is explicit in the prepared export as `options.responseMode: "lastNode"`.
   During the import check, execution succeeded but the editor chat displayed
   "Failed to receive response" until this setting was selected.

Node names used by code references must match the imported workflow. For
example, `$('Format Evidence')` and `$('When chat message received')` resolve by
node name. Preserve those names or update the referencing code.

## 4. Smoke test

Ask:

> What should I check when payments-api /charge returns 5xx errors and Stripe requests time out?

Save both Format Evidence and Render Cited Answer output from that execution.
Check that RB-001 is retrieved, citations resolve to its GitHub source, and
following RB-009 remains conditional on pool saturation. Verify source commands
and escalation thresholds manually. Do not equate a successful node execution
with a faithful answer.

The [recorded import check](import-verification.md) confirms that all three
exports were imported as copies in the existing Cloud instance. Ingestion
populated `second-responder-runbooks-52` with 12 records. The imported chat
then returned an answer, and retrieval execution 56 (parent 55) confirms that
it queried this new namespace and returned three documents. An independent-account
setup remains unverified. The repository retrieval export retains the original
development namespace `second-responder-runbooks-9`; set it to the namespace
created by your own ingestion.

## 5. Hosted chat and assignment evidence

The Chat Trigger supports Hosted Chat and a production Chat URL. Configure
authentication for the pilot and publish the workflow before using its
production URL. A localhost-only n8n instance needs a reachable deployment for
other engineers to access it. Capture screenshots of all three canvases and one
cited answer if the assignment requires them. Do not include credential screens.

Chat memory has not been implemented or verified. Passing a `sessionId` through
the formatter does not itself give Basic LLM Chain conversation history.
