<svelte:head>
    <title>Privacy Policy — zebraAFT</title>
    <meta
        name="description"
        content="Privacy Policy for zebraAFT Anonymous File Transfer."
    />
</svelte:head>

<div class="legal-page">
    <div class="legal-container">
        <a href="/" class="back">← Back to zebraAFT</a>

        <h1>Privacy Policy</h1>
        <p class="updated">Last updated: September 23, 2026</p>

        <p>
            This Privacy Policy explains how zebraAFT handles information when
            you use the anonymous file-transfer service.
        </p>

        <h2>1. Information We Handle</h2>

        <p>
            zebraAFT is designed so that you do not need to create an account,
            provide a name, or provide an email address to transfer files.
        </p>

        <p>
            When you create a Drop, the service stores information required to
            operate that Drop, including:
        </p>

        <ul>
            <li>A randomly generated Drop Code.</li>
            <li>A private delete token.</li>
            <li>The selected Drop lifetime.</li>
            <li>Creation and expiration timestamps.</li>
            <li>Uploaded file metadata such as filename and file identifier.</li>
            <li>The location of the associated file in private storage.</li>
        </ul>

        <h2>2. Uploaded Files</h2>

        <p>
            Uploaded files are stored in private cloud storage so that the
            zebraAFT backend can provide them when a valid Drop is accessed.
        </p>

        <p>
            File contents are not intended to be publicly accessible through a
            public storage URL.
        </p>

        <h2>3. No User Accounts</h2>

        <p>
            zebraAFT does not require traditional user accounts for its file
            transfer workflow. The service identifies Drops using randomly
            generated Drop Codes.
        </p>

        <h2>4. Drop Codes</h2>

        <p>
            A Drop Code acts as an access identifier for a Drop. Anyone who
            obtains the code may be able to access the Drop.
        </p>

        <p>
            Because zebraAFT does not require an account for normal file
            transfers, you should treat your Drop Code as information that
            should only be shared with intended recipients.
        </p>

        <h2>5. Delete Tokens</h2>

        <p>
            The creator of a Drop receives a separate delete token. This token
            is used to authorize deletion of the Drop.
        </p>

        <p>
            Do not publicly share your delete token.
        </p>

        <h2>6. Retention</h2>

        <p>
            Drops configured for 24-hour expiration are intended to be removed
            after their expiration time.
        </p>

        <p>
            Permanent Drops remain stored until they are deleted or otherwise
            removed as part of operating or maintaining the service.
        </p>

        <h2>7. Service Providers</h2>

        <p>
            zebraAFT uses third-party infrastructure providers to operate the
            service, including:
        </p>

        <ul>
            <li>Vercel for frontend hosting.</li>
            <li>Render for backend hosting.</li>
            <li>Supabase for PostgreSQL database services and file storage.</li>
        </ul>

        <p>
            These providers may process information as necessary to provide
            their infrastructure and services.
        </p>

        <h2>8. Cookies and Tracking</h2>

        <p>
            zebraAFT does not require cookies for its core file-transfer
            functionality.
        </p>

        <p>
            Third-party infrastructure or hosting services may have their own
            technical logging or operational practices.
        </p>

        <h2>9. Security</h2>

        <p>
            zebraAFT uses measures such as private object storage, server-side
            access to stored files, Drop validation, expiration checks, and
            separate delete tokens.
        </p>

        <p>
            No online service can guarantee absolute security. You should avoid
            uploading highly sensitive information unless you are comfortable
            with the risks associated with using an online file-transfer
            service.
        </p>

        <h2>10. Children's Privacy</h2>

        <p>
            zebraAFT is not specifically designed for children. Users should
            comply with the laws and requirements applicable to them when using
            the service.
        </p>

        <h2>11. Changes to This Policy</h2>

        <p>
            This Privacy Policy may be updated when the service or its data
            practices change. The updated version will be published on this
            page.
        </p>

        <h2>12. Contact</h2>

        <p>
            For privacy questions, contact the project maintainer through the
            project's official repository.
        </p>
    </div>
</div>

<style>
    .legal-page {
        min-height: 100vh;
        padding: 40px 20px;
        box-sizing: border-box;
    }

    .legal-container {
        max-width: 850px;
        margin: 0 auto;
        padding: 30px;
        background: #f0f0f0;
        border: 2px solid #315b8a;
        box-shadow:
            inset 1px 1px white,
            inset -1px -1px #777;
        font-family: "Courier New", monospace;
        color: #111;
        line-height: 1.6;
    }

    .back {
        display: inline-block;
        margin-bottom: 20px;
        color: #0000ee;
        text-decoration: underline;
    }

    h1 {
        margin: 0;
        font-size: 32px;
    }

    h2 {
        margin-top: 32px;
        font-size: 21px;
        color: #123f70;
    }

    .updated {
        color: #555;
        font-size: 14px;
    }

    li {
        margin: 8px 0;
    }
</style>