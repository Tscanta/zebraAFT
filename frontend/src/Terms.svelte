<svelte:head>
    <title>Terms of Service — zebraAFT</title>
    <meta
        name="description"
        content="Terms of Service for zebraAFT Anonymous File Transfer."
    />
</svelte:head>

<div class="legal-page">
    <div class="legal-container">
        <a href="/" class="back">← Back to zebraAFT</a>

        <h1>Terms of Service</h1>
        <p class="updated">Last updated: September 23, 2026</p>

        <p>
            Welcome to zebraAFT, an anonymous file-transfer service that allows
            users to temporarily share files using a Drop Code.
        </p>

        <h2>1. Acceptance of These Terms</h2>
        <p>
            By accessing or using zebraAFT, you agree to these Terms of Service.
            If you do not agree with these terms, please do not use the service.
        </p>

        <h2>2. The Service</h2>
        <p>
            zebraAFT allows users to create Drops, upload files, and access those
            files from another device using a Drop Code.
        </p>

        <p>
            Drops may either expire automatically after 24 hours or be kept
            permanently until deleted by the creator.
        </p>

        <h2>3. Your Responsibility</h2>
        <p>
            You are responsible for the files and other content that you upload
            to zebraAFT.
        </p>

        <p>You must not use zebraAFT to:</p>

        <ul>
            <li>Upload illegal content.</li>
            <li>Upload content that infringes another person's rights.</li>
            <li>Distribute malware, viruses, or other harmful software.</li>
            <li>Attempt to compromise, disrupt, or abuse the service.</li>
            <li>Attempt to gain unauthorized access to another Drop.</li>
            <li>Use the service for activities that violate applicable law.</li>
        </ul>

        <h2>4. Drop Codes</h2>
        <p>
            Drop Codes are intended to provide access to a Drop. Anyone who
            obtains a valid Drop Code may potentially access the files
            associated with that Drop.
        </p>

        <p>
            Do not share a Drop Code with people who should not have access to
            its contents.
        </p>

        <h2>5. File Deletion and Expiration</h2>
        <p>
            24-hour Drops are automatically removed after their expiration
            period. Permanent Drops remain available until they are deleted.
        </p>

        <p>
            The service may also remove files or Drops when necessary to
            maintain, secure, or operate the service.
        </p>

        <h2>6. Availability</h2>
        <p>
            zebraAFT is provided on an availability basis and may occasionally
            experience downtime, maintenance, errors, or interruptions.
        </p>

        <p>
            We do not guarantee that uploaded files will always remain
            available or that the service will always be accessible.
        </p>

        <h2>7. No Warranty</h2>
        <p>
            To the extent permitted by applicable law, zebraAFT is provided
            without warranties of any kind. You use the service at your own
            risk.
        </p>

        <h2>8. Limitation of Liability</h2>
        <p>
            To the extent permitted by applicable law, the operators of zebraAFT
            are not responsible for losses resulting from the use of the
            service, including loss of files, service interruptions, or
            unauthorized access resulting from a user's failure to protect
            their Drop Code.
        </p>

        <h2>9. Changes to the Service</h2>
        <p>
            zebraAFT may be modified, suspended, or discontinued at any time.
            These Terms may also be updated when necessary.
        </p>

        <h2>10. Contact</h2>
        <p>
            For questions about these Terms, contact the project maintainer
            through the project's official repository.
        </p>

        <h2>11. Governing Law</h2>
        <p>
            These Terms are intended as a general description of the rules for
            using zebraAFT. Applicable laws and regulations may vary depending
            on the user's location.
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