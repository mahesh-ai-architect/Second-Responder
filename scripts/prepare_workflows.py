"""Prepare reviewed n8n downloads for publication; originals stay in workflows/raw.

This scanner flags common secret patterns; it does not replace manual review.
Run from any directory: python3 scripts/prepare_workflows.py
"""
import copy
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'workflows' / 'raw'
SECRET_PATTERN = re.compile(
    r'(?i)(Bearer\s+[^\s"\']+|sk-[A-Za-z0-9_-]{16,}|'
    r'gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|'
    r'pcsk_[A-Za-z0-9_]{16,}|AKIA[A-Z0-9]{16})'
)
SENSITIVE_KEY = re.compile(
    r'(?i)^(api[_-]?key|authorization|password|secret|access[_-]?token|refresh[_-]?token)$'
)
CODE_FILES = {
    'Prepare Document': 'prepare-document.js',
    'Format Evidence': 'format-evidence.js',
    'Render Cited Answer': 'render-cited-answer.js',
}


def inspect_values(value, path='root'):
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEY.match(key) and child:
                raise ValueError(f'Manual review required: sensitive field at {path}.{key}')
            inspect_values(child, f'{path}.{key}')
        if str(value.get('name', '')).lower() in {'authorization', 'x-api-key', 'api-key'} and value.get('value'):
            raise ValueError(f'Manual review required: authentication header at {path}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_values(child, f'{path}[{index}]')
    elif isinstance(value, str) and SECRET_PATTERN.search(value):
        raise ValueError(f'Manual review required: possible secret at {path}')


def role_for(workflow):
    types = {node['type'] for node in workflow['nodes']}
    if '@n8n/n8n-nodes-langchain.chatTrigger' in types:
        return '03-chat.json'
    if 'n8n-nodes-base.executeWorkflowTrigger' in types:
        return '02-retrieval.json'
    if any(node['type'].endswith('.vectorStorePinecone') and
           node.get('parameters', {}).get('mode') == 'insert'
           for node in workflow['nodes']):
        return '01-ingestion.json'
    raise ValueError('Unrecognized workflow role; inspect the export manually.')


def prepare(original):
    workflow = copy.deepcopy(original)
    for key in ('id', 'versionId', 'versionCounter', 'meta', 'staticData',
                'createdAt', 'updatedAt', 'shared'):
        workflow.pop(key, None)
    workflow['active'] = False
    workflow['pinData'] = {}
    for node in workflow['nodes']:
        node.pop('credentials', None)
        node.pop('webhookId', None)
        params = node.get('parameters', {})
        if node['type'].endswith('.chatTrigger'):
            # Confirmed in the Cloud import check: return the final renderer output.
            params.setdefault('options', {})['responseMode'] = 'lastNode'
        if node['type'].endswith('.embeddingsOpenAi'):
            # Version 1.2 defaults to this model; make it explicit for reproduction.
            if 'model' not in params:
                if node.get('typeVersion') != 1.2:
                    raise ValueError('Confirm embedding default before pinning another node version.')
                params['model'] = 'text-embedding-3-small'
        if node.get('name') == 'Render Cited Answer':
            code = params.get('jsCode', '')
            marker = "// Loop over input items and add a new field called 'myNewField' to the JSON of each one"
            if marker in code:
                head, tail = code.split(marker, 1)
                expected = "for (const item of $input.all()) {\n  item.json.myNewField = 1;\n}\n\nreturn $input.all();"
                if tail.strip() != expected or not head.rstrip().endswith('}];'):
                    raise ValueError('Renderer boilerplate differs; inspect before removing it.')
                params['jsCode'] = head.rstrip() + '\n'
    inspect_values(workflow)
    return workflow


def validate_connections(workflow):
    names = [node['name'] for node in workflow['nodes']]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate node names make code references ambiguous.')
    for source, channels in workflow.get('connections', {}).items():
        if source not in names:
            raise ValueError(f'Unknown connection source: {source}')
        for outputs in channels.values():
            for edges in outputs:
                for edge in edges:
                    if edge['node'] not in names:
                        raise ValueError(f'Unknown connection target: {edge["node"]}')


def main():
    records = []
    prepared = set()
    originals = {}
    for path in sorted(RAW.glob('*.json')):
        original = json.loads(path.read_text())
        if not isinstance(original.get('nodes'), list):
            raise ValueError(f'{path.name} is not a full workflow export.')
        destination = role_for(original)
        if destination in prepared:
            raise ValueError(f'Multiple raw files represent {destination}; keep one reviewed snapshot.')
        prepared.add(destination)
        originals[destination] = original
        workflow = prepare(original)
        validate_connections(workflow)
        target = ROOT / 'workflows' / destination
        target.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + '\n')
        extracted = []
        for node in workflow['nodes']:
            filename = CODE_FILES.get(node['name'])
            code = node.get('parameters', {}).get('jsCode')
            if filename and code is not None:
                output = ROOT / 'code' / filename
                output.parent.mkdir(exist_ok=True)
                output.write_text(code.rstrip() + '\n')
                extracted.append(f'code/{filename}')
            if node['type'].endswith('.chainLlm'):
                messages = node.get('parameters', {}).get('messages', {}).get('messageValues', [])
                system = [m['message'] for m in messages
                          if str(m.get('type', 'System')).lower() == 'system']
                expected = (ROOT / 'prompts/system-v3.txt').read_text()
                if len(system) != 1 or ' '.join(system[0].split()) != ' '.join(expected.split()):
                    raise ValueError('Exported System message does not match the documented v3 prompt.')
        records.append({
            'raw_filename': path.name,
            'raw_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'repository_file': f'workflows/{destination}',
            'repository_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'node_count': len(workflow['nodes']),
            'credential_bindings_removed': sum(bool(n.get('credentials')) for n in original['nodes']),
            'code_files': extracted,
        })
        print(f'Prepared workflows/{destination}: {len(workflow["nodes"])} nodes')
    dependencies = []
    by_id = {workflow.get('id'): name for name, workflow in originals.items() if workflow.get('id')}
    for name, workflow in originals.items():
        for node in workflow['nodes']:
            if node['type'] != 'n8n-nodes-base.executeWorkflow':
                continue
            params = node.get('parameters', {})
            selected = params.get('workflowId', {})
            selected = selected.get('value') if isinstance(selected, dict) else selected
            target = by_id.get(selected)
            input_keys = sorted(params.get('workflowInputs', {}).get('value', {}))
            if target:
                declared = {entry['name'] for trigger in originals[target]['nodes']
                            if trigger['type'] == 'n8n-nodes-base.executeWorkflowTrigger'
                            for entry in trigger.get('parameters', {}).get('workflowInputs', {}).get('values', [])}
                if not set(input_keys).issubset(declared):
                    raise ValueError('Caller passes inputs missing from the exported retrieval trigger.')
            dependencies.append({
                'caller': f'workflows/{name}',
                'node': node['name'],
                'target': f'workflows/{target}' if target else None,
                'input_keys': input_keys,
                'resolved_against_raw_exports': target is not None,
                'reselect_target_after_import': True,
            })
    report = {
        'scope': 'Local JSON structure and code review; no external API calls or n8n import execution.',
        'transformations': [
            'Remove credential bindings; reconnect credentials after import.',
            'Remove root instance/version metadata and deployed webhook identifiers.',
            'Clear pinned data and keep exported workflows inactive.',
            'Make omitted embeddingsOpenAi 1.2 model default explicit.',
            'Set Chat Trigger responseMode to lastNode, as confirmed by the user import check.',
            'Remove unreachable renderer sample code after the final return.',
            'Preserve node names, connections, System message, and retrieval workflow reference.',
        ],
        'workflows': records,
        'workflow_dependencies': dependencies,
        'missing_exports': sorted({'01-ingestion.json', '02-retrieval.json', '03-chat.json'} - prepared),
    }
    (ROOT / 'workflows/export-review.json').write_text(json.dumps(report, indent=2) + '\n')
    if report['missing_exports']:
        print('Still needed: ' + ', '.join(report['missing_exports']))


if __name__ == '__main__':
    main()
