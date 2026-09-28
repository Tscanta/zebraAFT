
<svelte:head>
  <title>FAQs - zebraAFT</title>
  <meta
    name="description"
    content="Frequently asked questions about using zebraAFT."
  />
</svelte:head>

<div class="info-page">
  <h1>Frequently Asked Questions</h1>

  <h2>Do I need an account?</h2>
  <p>No. You can create and access Drops without registering.</p>

  <h2>How do I transfer files?</h2>
  <p>
    Select files, create a Drop, and enter its Drop Code on
    the other device.
  </p>

  <h2>What is a Drop Code?</h2>
  <p>
    It is an eight-character code used to find and access
    a Drop.
  </p>

  <h2>How long do Drops last?</h2>
  <p>
    You can choose 24-hour expiration or permanent storage.
    Permanent Drops remain until deleted or affected by
    service availability or storage policies.
  </p>

  <h2>Can I upload more files later?</h2>
  <p>
    Yes. Open the Drop and use the Add Files option.
  </p>

  <h2>Can anyone delete my Drop?</h2>
  <p>
    The creator can delete the Drop using the creator's
    delete token. Someone with only the Drop Code can
    access and upload files but cannot delete the Drop.
  </p>

  <h2>Can I access a Drop from another device?</h2>
  <p>
    Yes. Open zebraAFT on the other device and enter
    the Drop Code.
  </p>

  <h2>Are my files stored forever?</h2>
  <p>
    Not necessarily. Files in 24-hour Drops are scheduled
    for deletion after expiration. Permanent Drops have
    no automatic expiration, but are not a guarantee of
    indefinite availability.
  </p>

  <h2>Is zebraAFT completely private?</h2>
  <p>
    A Drop Code is a means of accessing a Drop, not a
    password. Anyone who obtains the code may be able
    to access its contents. Do not upload sensitive files
    unless you understand the risks.
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
    margin-top: 24px;
    font-size: 18px;
  }

  .back-link {
    display: inline-block;
    margin-top: 24px;
    color: #174f8a;
  }
</style>