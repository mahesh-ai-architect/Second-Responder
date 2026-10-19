const chat = $('When chat message received').first().json;

const documents = $input.all()
  .map(item => item.json)
  .filter(item =>
    typeof item.document?.pageContent === 'string' &&
    item.document.pageContent.trim().length > 0
  );

const sources = documents.map((item, index) => ({
  id: `S${index + 1}`,
  filename: item.document.metadata?.filename ?? 'Unknown runbook',
  url: item.document.metadata?.source ?? '',
  text: item.document.pageContent,
  score: item.score
}));

const context = sources.map(source =>
  `[${source.id}] ${source.filename}\n${source.text}`
).join('\n\n---\n\n');

return [{
  json: {
    question: chat.chatInput,
    sessionId: chat.sessionId ?? '',
    context: context || 'No runbook evidence was retrieved.',
    sources
  }
}];
