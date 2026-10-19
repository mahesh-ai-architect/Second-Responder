const answer = $input.first().json.output;
const sources = $('Format Evidence').first().json.sources ?? [];
const byId = new Map(sources.map(source => [source.id, source]));

const fallback = () => [{
  json: {
    output: 'I could not produce an answer with valid runbook references. Please provide the service name and exact alert.'
  }
}];

if (!answer || !Array.isArray(answer.steps)) {
  return fallback();
}

if (answer.status === 'needs_clarification') {
  if (
    answer.steps.length !== 0 ||
    typeof answer.clarifying_question !== 'string' ||
    !answer.clarifying_question.trim()
  ) {
    return fallback();
  }

  return [{
    json: { output: answer.clarifying_question.trim() }
  }];
}

if (answer.status !== 'answered' || !answer.steps.length) {
  return fallback();
}

const sections = [
  'First checks',
  'Conditional remediation',
  'Escalation',
  'After resolution'
];

const validSource = id => {
  const source = byId.get(id);
  return (
    /^S\d+$/.test(id) &&
    typeof source?.url === 'string' &&
    source.url.startsWith(
      'https://github.com/mahesh-ai-architect/Second-Responder/blob/'
    )
  );
};

for (const step of answer.steps) {
  if (
    !sections.includes(step.section) ||
    typeof step.text !== 'string' ||
    !step.text.trim() ||
    !Array.isArray(step.source_ids) ||
    !step.source_ids.length ||
    !step.source_ids.every(validSource)
  ) {
    return fallback();
  }
}

const blocks = sections.flatMap(section => {
  const steps = answer.steps.filter(step => step.section === section);
  if (!steps.length) return [];

  const lines = steps.map((step, index) => {
    const citations = [...new Set(step.source_ids)]
      .map(id => `[${id}](${byId.get(id).url})`)
      .join(' ');

    return `${index + 1}. ${step.text.trim()} ${citations}`;
  });

  return [`### ${section}\n\n${lines.join('\n\n')}`];
});

return [{
  json: { output: blocks.join('\n\n') }
}];
