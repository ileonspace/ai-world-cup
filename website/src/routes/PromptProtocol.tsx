export function PromptProtocol() {
  return (
    <div className="prose max-w-none dark:prose-invert">
      <h1>Prompt protocol</h1>
      <p>AI World Cup does not call LLM APIs. The repository generates one standardized full-tournament prompt, and the user manually sends the exact same prompt to each model.</p>
      <h2>Manual submission protocol</h2>
      <ol>
        <li>Generate the tournament prompt from the repo.</li>
        <li>Copy the full prompt without edits.</li>
        <li>Send the same prompt to every model.</li>
        <li>Save each raw answer exactly as returned.</li>
        <li>Import the response with the CLI.</li>
        <li>Keep prompt version and data snapshot fixed for fair comparison.</li>
      </ol>
      <h2>Fairness rules</h2>
      <p>Every model receives the same fixture context, data snapshot ID, prompt version, output schema, and JSON-only instructions.</p>
    </div>
  );
}
