const file = $json;

const text = Buffer
  .from(file.content, 'base64')
  .toString('utf8');

return {
  json: {
    text,
    filename: file.name,
    source: file.html_url,
    path: file.path,
    git_sha: file.sha
  }
};
