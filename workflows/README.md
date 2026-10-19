# n8n workflow exports

All three reviewed exports are present. Keep workflow JSON as the source of truth for configuration,
connections, JavaScript, prompts, and sub-node settings. Extracted `.js` copies
in `code/` match the reviewed export parameters.

| File | Current state |
| --- | --- |
| `01-ingestion.json` | Prepared from the actual 10-node download |
| `02-retrieval.json` | Prepared from the actual 3-node download; query input and namespace checked |
| `03-chat.json` | Prepared from the actual 7-node download; System message matches v3 after whitespace normalization |

See [export-review.json](export-review.json) for hashes, removed credential-binding
counts, and dependency checks. No required exports are missing. Preparation removes credential bindings and root
instance/version metadata, removes the deployed webhook identifier, clears pinned
data, and keeps workflows inactive. Reconnect credentials after import.

Preparation also explicitly sets Chat Trigger response mode to **When Last Node
Finishes** (`options.responseMode: "lastNode"`). The user confirmed that this
resolved a chat-delivery error in the imported copy. See the
[import verification record](../docs/import-verification.md).

Both embedding nodes omitted their model because version 1.2 of that node
defaults to `text-embedding-3-small`. The reviewed copies make it explicit. The
chat model is `gpt-5-mini`, preserved as exported for reproduction.

The renderer contained unused sample code after its unconditional final return.
That unreachable block was removed. Local tests compare old/new outputs for
answered, malformed, and clarification inputs. No live n8n workflow was edited.

Embedding default reference: [n8n source](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/embeddings/EmbeddingsOpenAI/EmbeddingsOpenAi.node.ts).

The chat export's selected sub-workflow ID matches the retrieval download's ID,
and the passed `query` field matches the retrieval trigger's declared input.
Those checks establish the original linkage; after importing into another n8n
instance, reselect its newly imported retrieval workflow. Retrieval points at
the observed development namespace `second-responder-runbooks-9`, with no leading
or trailing whitespace. A fresh ingestion run requires updating that namespace.

## Export from n8n

For each of the three workflows:

1. Open the workflow and confirm it contains the version used for your tests.
2. Choose the workflow menu (`...`) in the canvas header, then **Download**.
3. Save the original under `workflows/raw/` while reviewing it. That directory is
   ignored by Git. Do not export a credentials backup for the assignment.
4. Add a reviewed copy using these filenames:

| File | Must contain |
| --- | --- |
| `01-ingestion.json` | GitHub fetch/filter/decode, loop, Pinecone insert, embedding model, data loader, text splitter |
| `02-retrieval.json` | Execute Sub-workflow Trigger with `query` input, Pinecone Get Many, embedding model |
| `03-chat.json` | Chat Trigger, Execute Sub-workflow, Format Evidence, Basic LLM Chain, chat model, structured parser, Render Cited Answer |

Export the entire workflow, including attached model/parser/loader/splitter
nodes, rather than copying only the main-line nodes.

## Review before committing

Check for hardcoded API keys, tokens, passwords, authorization headers, sensitive
endpoint URLs, and personal data in node parameters, pinned data, and saved
examples. Remove pinned examples unless deliberately included as synthetic test
fixtures. Inspect any embedded code for literal credentials.

Exports include credential names and IDs; these references are not the secret
credential values, but names can disclose identifying information. Anonymize
names if needed. If credential references are removed, document that the
importer must reconnect credentials. Check workflow metadata and webhook paths
before publishing. JSON syntax validation alone is not a secrets review.

Do not remove Execute Sub-workflow references blindly: the chat workflow's node
references retrieval. On another instance, select the newly imported
retrieval workflow in that node. Export IDs are not portable account access.

To prepare reviewed copies after manually inspecting new raw downloads:

```sh
python3 scripts/prepare_workflows.py
```

The helper reads the ignored raw folder, prepares available workflow roles,
extracts JavaScript, and records a manifest. Its common-pattern secret scan is
not a complete security audit. Keep one raw snapshot per workflow role and
inspect the generated diff before committing.

## Import and verify

Import ingestion, then retrieval, then chat through **Import from File**.
Reconnect credentials, set the populated Pinecone namespace, and reselect the
retrieval workflow from the chat node's workflow list. Verify `query` receives
`{{ $json.chatInput }}`. Test through the editor before publishing hosted chat.

Official reference: [n8n export and import](https://docs.n8n.io/workflows/export-import/).
