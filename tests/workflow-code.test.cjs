// Local tests of exported Code nodes. No model, Pinecone, or GitHub calls.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const load = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const ingestion = load('workflows/01-ingestion.json');
const chat = load('workflows/03-chat.json');
const retrievalPath = path.join(root, 'workflows/02-retrieval.json');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const codeFor = (workflow, name) => workflow.nodes.find(n => n.name === name).parameters.jsCode;
const source = {
  id: 'S1', filename: 'RB-001-payments-api-5xx.md',
  url: 'https://github.com/mahesh-ai-architect/Second-Responder/blob/main/runbooks/RB-001-payments-api-5xx.md',
  text: 'Pool saturation: follow RB-009.', score: 0.67,
};
const fallback = 'I could not produce an answer with valid runbook references. Please provide the service name and exact alert.';

async function format(items) {
  return new AsyncFunction('$input', '$', codeFor(chat, 'Format Evidence'))(
    { all: () => items.map(json => ({ json })) },
    name => {
      assert.equal(name, 'When chat message received');
      return { first: () => ({ json: { chatInput: 'Payments alert?', sessionId: 'test-session' } }) };
    },
  );
}

async function render(answer, sources = [source], code = codeFor(chat, 'Render Cited Answer')) {
  return new AsyncFunction('$input', '$', code)(
    { first: () => ({ json: { output: answer } }), all: () => [{ json: { output: answer } }] },
    name => {
      assert.equal(name, 'Format Evidence');
      return { first: () => ({ json: { sources } }) };
    },
  );
}

const supportedAnswer = () => ({
  status: 'answered', clarifying_question: '',
  steps: [{ section: 'Conditional remediation', text: 'If the pool is saturated, follow RB-009.', source_ids: ['S1'] }],
});

test('Prepare Document decodes text and preserves source metadata', async () => {
  const text = 'Runbook text with Unicode: café';
  const file = { content: Buffer.from(text).toString('base64'), name: 'RB-001.md',
    html_url: source.url, path: 'runbooks/RB-001.md', sha: 'test-blob-sha' };
  const result = await new AsyncFunction('$json', 'Buffer', codeFor(ingestion, 'Prepare Document'))(file, Buffer);
  assert.deepEqual(result.json, { text, filename: file.name, source: file.html_url, path: file.path, git_sha: file.sha });
});

test('Format Evidence keeps usable documents, source mapping, and real newlines', async () => {
  const results = await format([
    { document: { pageContent: source.text, metadata: { filename: source.filename, source: source.url } }, score: source.score },
    {}, { document: { pageContent: '  ' } },
    { document: { pageContent: 'Second document', metadata: {} }, score: 0.2 },
  ]);
  assert.equal(results.length, 1);
  const value = results[0].json;
  assert.equal(value.question, 'Payments alert?');
  assert.equal(value.sessionId, 'test-session');
  assert.deepEqual(value.sources.map(s => s.id), ['S1', 'S2']);
  assert.equal(value.sources[0].url, source.url);
  assert.equal(value.context, `[S1] ${source.filename}\n${source.text}\n\n---\n\n[S2] Unknown runbook\nSecond document`);
});

test('Format Evidence emits an explicit empty-evidence item', async () => {
  const [{ json }] = await format([{}]);
  assert.deepEqual(json.sources, []);
  assert.equal(json.context, 'No runbook evidence was retrieved.');
});

test('Renderer groups steps and creates citations from retrieved URLs', async () => {
  const answer = supportedAnswer();
  answer.steps.push({ section: 'First checks', text: 'Check the pool.', source_ids: ['S1', 'S1'] });
  const [{ json }] = await render(answer);
  assert.ok(json.output.startsWith('### First checks\n\n1. Check the pool.'));
  assert.equal(json.output.match(/\[S1\]\(/g).length, 2);
  assert.ok(json.output.includes(`### Conditional remediation\n\n1. If the pool is saturated, follow RB-009. [S1](${source.url})`));
});

test('Renderer rejects unknown source IDs', async () => {
  const answer = supportedAnswer();
  answer.steps[0].source_ids = ['S99'];
  assert.equal((await render(answer))[0].json.output, fallback);
});

test('Renderer rejects a citation outside the configured repository', async () => {
  const sources = [{ ...source, url: 'https://example.com/runbook' }];
  assert.equal((await render(supportedAnswer(), sources))[0].json.output, fallback);
});

test('Renderer rejects steps missing citations or using an unknown section', async () => {
  const missing = supportedAnswer();
  missing.steps[0].source_ids = [];
  assert.equal((await render(missing))[0].json.output, fallback);
  const invalid = supportedAnswer();
  invalid.steps[0].section = 'Invented section';
  assert.equal((await render(invalid))[0].json.output, fallback);
});

test('Renderer handles structured clarification and rejects contradictory shape', async () => {
  const answer = { status: 'needs_clarification', steps: [], clarifying_question: ' Which service? ' };
  assert.equal((await render(answer))[0].json.output, 'Which service?');
  answer.steps = supportedAnswer().steps;
  assert.equal((await render(answer))[0].json.output, fallback);
  assert.equal((await render(undefined))[0].json.output, fallback);
});

test('Reference validation alone does not detect unsupported instructions', async () => {
  const answer = supportedAnswer();
  answer.steps[0].text = 'An invented instruction not supported by the source.';
  assert.ok((await render(answer))[0].json.output.includes(answer.steps[0].text));
});

test('Standalone code copies match the reviewed workflow parameters', () => {
  for (const [workflow, name, file] of [
    [ingestion, 'Prepare Document', 'prepare-document.js'],
    [chat, 'Format Evidence', 'format-evidence.js'],
    [chat, 'Render Cited Answer', 'render-cited-answer.js'],
  ]) {
    assert.equal(fs.readFileSync(path.join(root, 'code', file), 'utf8').trimEnd(), codeFor(workflow, name).trimEnd());
  }
});

test('Retrieval and chat agree on the query input contract', { skip: !fs.existsSync(retrievalPath) }, () => {
  const retrieval = load('workflows/02-retrieval.json');
  const trigger = retrieval.nodes.find(n => n.type === 'n8n-nodes-base.executeWorkflowTrigger');
  const vector = retrieval.nodes.find(n => n.type.endsWith('.vectorStorePinecone'));
  const call = chat.nodes.find(n => n.type === 'n8n-nodes-base.executeWorkflow');
  const chatTrigger = chat.nodes.find(n => n.type.endsWith('.chatTrigger'));
  assert.equal(chatTrigger.parameters.options.responseMode, 'lastNode');
  assert.ok(trigger.parameters.workflowInputs.values.some(v => v.name === 'query'));
  assert.equal(call.parameters.workflowInputs.value.query, '={{ $json.chatInput }}');
  assert.equal(call.parameters.options.waitForSubWorkflow, true);
  assert.equal(vector.parameters.prompt, '={{ $json.query }}');
  assert.equal(vector.parameters.topK, 3);
  const report = load('workflows/export-review.json');
  assert.deepEqual(report.missing_exports, []);
  assert.equal(report.workflow_dependencies[0].target, 'workflows/02-retrieval.json');
  assert.equal(report.workflow_dependencies[0].resolved_against_raw_exports, true);
});

test('Embedding configuration agrees across ingestion/retrieval and namespace has no extra spaces', { skip: !fs.existsSync(retrievalPath) }, () => {
  const retrieval = load('workflows/02-retrieval.json');
  const first = ingestion.nodes.find(n => n.type.endsWith('.embeddingsOpenAi')).parameters;
  const second = retrieval.nodes.find(n => n.type.endsWith('.embeddingsOpenAi')).parameters;
  assert.equal(second.model, first.model);
  assert.equal(second.options.dimensions, first.options.dimensions);
  const insert = ingestion.nodes.find(n => n.type.endsWith('.vectorStorePinecone')).parameters;
  const query = retrieval.nodes.find(n => n.type.endsWith('.vectorStorePinecone')).parameters;
  assert.equal(query.pineconeIndex.value, insert.pineconeIndex.value);
  const namespace = query.options.pineconeNamespace;
  assert.ok(namespace.length > 0);
  assert.equal(namespace, namespace.trim());
});

const rawChat = path.join(root, 'workflows/raw/Second Responder - Support Chat.json');
test('Removing unreachable sample code preserves renderer output', { skip: !fs.existsSync(rawChat) }, async () => {
  const original = JSON.parse(fs.readFileSync(rawChat, 'utf8'));
  const oldCode = codeFor(original, 'Render Cited Answer');
  for (const answer of [supportedAnswer(), undefined,
    { status: 'needs_clarification', steps: [], clarifying_question: 'Which alert?' }]) {
    assert.deepEqual(await render(answer), await render(answer, [source], oldCode));
  }
});
