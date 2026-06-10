export function About() {
  return (
    <div className="prose max-w-none dark:prose-invert">
      <h1>About AI World Cup</h1>
      <p>AI World Cup compares LLM predictions for FIFA World Cup 2026 with a reproducible manual benchmark.</p>
      <h2>How it works</h2>
      <p>The Python CLI syncs football data, generates one shared full-tournament prompt, imports manually saved model responses, validates JSON, and exports static website data.</p>
      <h2>Scoring</h2>
      <p>Scoring covers exact scores, match outcomes, group standings, knockout progression, and final rankings as real results become available.</p>
      <h2>Limitations</h2>
      <p>Model outputs can be malformed or inconsistent. The benchmark stores validation warnings so readers can evaluate prediction quality and schema discipline.</p>
      <p>This project is for research and entertainment. It is not betting advice.</p>
    </div>
  );
}
