
<svelte:head>
  <title>About - zebraAFT</title>
  <meta
    name="description"
    content="Learn about zebraAFT, a simple anonymous file transfer tool."
  />
</svelte:head>

<div class="info-page">
  <h1>About zebraAFT</h1>

  <p class="subtitle">Same files. Different places. No accounts.</p>

  <h2>What is zebraAFT?</h2>
  <p>
    zebraAFT is a simple file transfer tool that lets you move files
    between devices using a short Drop Code.
  </p>

  <p>
    Upload files on one device, open the Drop on another device,
    and download what you need. No account is required.
  </p>

  <h2>Why zebraAFT?</h2>
  <p>
    Moving files between devices should be simple. zebraAFT was
    created to make file transfers quick, accessible, and
    straightforward.
  </p>

  <h2>How it works</h2>
  <ol>
    <li>Select files and create a Drop.</li>
    <li>Copy the generated Drop Code.</li>
    <li>Enter the code on another device.</li>
    <li>Download or add files.</li>
  </ol>

  <p class="note">
    Drops can be configured to expire after 24 hours or remain
    until manually deleted.
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

  .note {
    background: #e5eff9;
    border: 1px solid #8caaca;
    padding: 12px;
  }

  .back-link {
    display: inline-block;
    margin-top: 24px;
    color: #174f8a;
  }
</style>