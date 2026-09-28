
<svelte:head>
  <title>Source - zebraAFT</title>
  <meta
    name="description"
    content="Explore the source code and technology behind zebraAFT."
  />
</svelte:head>

<div class="info-page">
  <h1>Source & Credits</h1>

  <p class="subtitle">
    Built on the web, for the web.
  </p>

  <h2>Source Code</h2>
  <p>
    Explore the zebraAFT project, browse the code, and
    follow its development on GitHub.
  </p>

  <a
    class="source-button"
    href="https://github.com/Tscanta/anonymous-file-transfer"
    target="_blank"
    rel="noopener noreferrer"
  >
    View on GitHub →
  </a>

  <h2>Technology</h2>
  <ul>
    <li>Svelte — frontend interface</li>
    <li>TypeScript — frontend logic</li>
    <li>FastAPI — backend API</li>
    <li>Supabase — database and file storage</li>
    <li>Vercel — frontend hosting</li>
    <li>Render — backend hosting</li>
  </ul>

  <h2>About the project</h2>
  <p>
    zebraAFT is an independent project built to make
    transferring files between devices simple.
  </p>

  <p>
    For bug reports, suggestions, or contributions,
    visit the GitHub repository.
  </p>

  <a class="back-link" href="/">← Back to home</a>
</div>

<style>
  .info-page {
    padding: 24px;
    font-family: "Courier New", monospace;
    line-height: 1.7;
    color: #172d45;
  }

  h1 {
    font-size: 28px;
    border-bottom: 2px solid #7298bd;
    padding-bottom: 10px;
  }

  h2 {
    margin-top: 26px;
    font-size: 19px;
  }

  .subtitle {
    color: #526f8c;
    font-weight: bold;
  }

  .source-button {
    display: inline-block;
    margin: 12px 0;
    padding: 10px 16px;
    background: #dceafa;
    border: 2px outset #a4bfdc;
    color: #174f8a;
    text-decoration: none;
  }

  .back-link {
    display: inline-block;
    margin-top: 24px;
    color: #174f8a;
  }
</style>