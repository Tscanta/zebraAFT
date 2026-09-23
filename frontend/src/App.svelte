<script lang="ts">
  import { createDrop, uploadFile, getDrop, deleteDrop } from "./lib/api";
  import { onMount } from "svelte";
  import QRCode from "qrcode";

  let selectedFiles: File[] = [];
  let dropCode = "";
  let deleteToken = "";
  let dropLifetime = "24h";

  let creating = false;
  let error = "";

  let openedDrop: {
  drop_id: string;
  created_at: string;
  expires_at: string | null;
  files: {
    file_id: string;
    filename: string;
  }[];
} | null = null;

// Copy Drop Code
let codeCopied = false; 

//QR 
let showQr = false;
let qrCodeUrl = "";

let opening = false;
let openError = "";

let dropFiles: File[] = [];

let uploading = false;
let uploadError = "";

let uploadProgress = 0;
let currentUpload = "";

async function toggleQr() {
  if (!openedDrop) {
    return;
  }

  if (showQr) {
    showQr = false;
    return;
  }

  try {
    qrCodeUrl = await QRCode.toDataURL(
      openedDrop.drop_id
    );

    showQr = true;
  } catch (err) {
    console.error("Could not generate QR code:", err);
  }
}

async function copyDropCode() {
  if (!openedDrop) {
    return;
  }

  try {
    await navigator.clipboard.writeText(
      openedDrop.drop_id
    );

    codeCopied = true;

    setTimeout(() => {
      codeCopied = false;
    }, 2000);

  } catch (err) {
    console.error("Could not copy Drop code:", err);
  }
}

async function openDropFromUrl() {
  const path = window.location.pathname;

  if (!path.startsWith("/drop/")) {
    return;
  }

  const dropId = path
    .replace("/drop/", "")
    .trim()
    .toUpperCase();

  if (!dropId) {
    return;
  }

  dropCode = dropId;
  opening = true;
  openError = "";
  openedDrop = null;

  try {
    const data = await getDrop(dropId);
    openedDrop = data;
  } catch (err) {
    console.error(err);

    if (err instanceof Error) {
      if (err.message === "Drop not found") {
        openError =
          "Drop not found. It may have expired, been deleted, or never existed.";
      } else {
        openError = err.message;
      }
    } else {
      openError = "Could not open Drop.";
    }
  } finally {
    opening = false;
  }
}
onMount(() => {
  openDropFromUrl();
});

function formatDropDate(date: string) {
  return new Date(date).toLocaleString();
}

function handleDropFiles(event: Event) {
  const input = event.target as HTMLInputElement;

  if (input.files) {
    dropFiles = Array.from(input.files);
  }
}

async function handleUploadFiles() {
  
  if (!openedDrop || dropFiles.length === 0) {
    return;
  }

  uploading = true;
  uploadError = "";
  uploadProgress = 0;
  currentUpload = "";

  try {
    const totalFiles = dropFiles.length;

    for (let i = 0; i < totalFiles; i++) {
      const file = dropFiles[i];

      currentUpload = file.name;

      await uploadFile(
        openedDrop.drop_id,
        file
      );

      uploadProgress = i + 1;
    }

    // Refresh the Drop
    const updatedDrop = await getDrop(
      openedDrop.drop_id
    );

    openedDrop = updatedDrop;

    // Clear selected files
    dropFiles = [];
    currentUpload = "";

  } catch (err) {
    console.error(err);

    if (err instanceof Error) {
      uploadError = err.message;
    } else {
      uploadError = "Could not upload files.";
    }

  } finally {
    uploading = false;
  }
}

function isImage(filename: string) {
  return /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(filename);
}
function getFileType(filename: string) {
  const extension = filename
    .split(".")
    .pop()
    ?.toLowerCase();

  if (!extension) {
    return "FILE";
  }

  const types: Record<string, string> = {
    pdf: "PDF",

    mp4: "VIDEO",
    avi: "VIDEO",
    mov: "VIDEO",
    mkv: "VIDEO",
    webm: "VIDEO",

    mp3: "AUDIO",
    wav: "AUDIO",
    ogg: "AUDIO",
    flac: "AUDIO",

    zip: "ZIP",
    rar: "ZIP",
    "7z": "ZIP",
    tar: "ZIP",
    gz: "ZIP",

    psd: "PSD",

    py: "CODE",
    js: "CODE",
    ts: "CODE",
    jsx: "CODE",
    tsx: "CODE",
    html: "CODE",
    css: "CODE",
    json: "CODE",

    doc: "DOC",
    docx: "DOC",

    txt: "TEXT",

    xls: "XLS",
    xlsx: "XLS",

    ppt: "PPT",
    pptx: "PPT"
  };
  return types[extension] ?? extension.toUpperCase();
}


  function handleFiles(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files) {
      selectedFiles = Array.from(input.files);
    }
  }

async function handleCreateDrop() {
  if (selectedFiles.length === 0) {
    return;
  }

  creating = true;
  error = "";

  try {
    // 1. Create the Drop
    const drop = await createDrop(dropLifetime);

    dropCode = drop.drop_id;
    deleteToken = drop.delete_token;

    // 2. Upload every selected file
    for (const file of selectedFiles) {
      await uploadFile(dropCode, file);
    }

    // 3. Automatically open the Drop
    const opened = await getDrop(dropCode);

    openedDrop = opened;

  } catch (err) {
    console.error("CREATE DROP ERROR:", err);

    if (err instanceof Error) {
      error = err.message;
    } else {
      error = "Could not create drop or upload files.";
    }

  } finally {
    creating = false;
  }
}

  async function handleOpenDrop() {
    if (!dropCode.trim()) {
      openError = "Please enter a drop code.";
      return;
    }

    opening = true;
    openError = "";
    openedDrop = null;

    try {
      const data = await getDrop(
        dropCode.trim().toUpperCase()
      );

      openedDrop = data;

    } catch (err) {
      console.error(err);

      if (err instanceof Error) {
        if (err.message === "Drop not found") {
          openError =
            "Drop not found. It may have expired, been deleted, or never existed.";
        } else {
          openError = err.message;
        }
      } else {
        openError = "Could not open Drop.";
      }

    } finally {
      opening = false;
    }
  }

  async function handleDeleteDrop() {
  if (!openedDrop || !deleteToken) {
    return;
  }

  const confirmed = confirm(
    "Delete this Drop?\n\nAll files in this Drop will be permanently deleted."
  );

  if (!confirmed) {
    return;
  }

  try {
    await deleteDrop(
      openedDrop.drop_id,
      deleteToken
    );

    openedDrop = null;
    dropCode = "";
    deleteToken = "";

  } catch (err) {
    console.error(err);

    if (err instanceof Error) {
      uploadError = err.message;
    } else {
      uploadError = "Could not delete Drop.";
    }
  }
  }


</script>

<svelte:head>
  <title>zebraAFT - Anonymous File Transfer</title>
</svelte:head>

<div class="page">

  <header class="header">
    <div class="logo">
      <span class="logo-main">zebra<span>AFT</span></span>
      <span class="logo-sub">anonymous file transfer</span>
    </div>

    <div class="tagline">
      same files.<br />
      different places.<br />
      no accounts.
    </div>
  </header>


  <div class="layout">

    <aside class="sidebar">

      <section class="panel">
        <div class="panel-title">:: navigation</div>

        <div class="nav">
          <a href="/">&gt; home</a>
          <a href="/">&gt; about</a>
          <a href="/">&gt; faq</a>
          <a href="/">&gt; source</a>
        </div>
      </section>


      <section class="panel">
        <div class="panel-title">:: status</div>

        <div class="status">
          <div>
            <span class="status-light"></span>
            server online
          </div>

          <div>
            <span class="status-light"></span>
            no login required
          </div>

          <div>
            <span class="status-light"></span>
            anonymous mode
          </div>
        </div>
      </section>

    </aside>


    <main class="content">

      <section class="panel welcome">

        <div class="panel-title">
          :: welcome to zebraAFT
        </div>

        <div class="welcome-body">

          <h1>Share files between devices.</h1>

          <p>
            No accounts. No tracking. Just files.
          </p>


          <div class="action">
            <label class="file-picker">
              📁 &nbsp; Select Files

              <input
                type="file"
                multiple
                onchange={handleFiles}
              />
            </label>

            <small>
              Select the files you want to transfer.
            </small>

            <div class="drop-lifetime">
              <div class="lifetime-title">
                Drop lifetime
              </div>

              <label class="lifetime-option">
                <input
                  type="radio"
                  name="lifetime"
                  value="24h"
                  bind:group={dropLifetime}
                />
                Expire after 24 hours
              </label>

              <label class="lifetime-option">
                <input
                  type="radio"
                  name="lifetime"
                  value="permanent"
                  bind:group={dropLifetime}
                />
                Keep permanently
              </label>

            </div>


            {#if selectedFiles.length > 0}

              <div class="selected-files">

                <div class="selected-title">
                  {selectedFiles.length} file(s) selected:
                </div>

                {#each selectedFiles as file}
                  <div class="file-item">
                    📄 {file.name}
                  </div>
                {/each}
              </div>
              <button
                class="retro-button"
                onclick={handleCreateDrop}
                disabled={creating}
              >
                {creating ? "Creating Drop..." : "📃  Create Drop"}
              </button>

              {#if dropCode}
                <div class="drop-created">

                  <div class="drop-created-title">
                    DROP CREATED!
                  </div>

                  <div class="drop-code">
                    {dropCode}
                  </div>

                  <p>
                    Your files are ready.
                    Enter this code on another device.
                  </p>

                </div>
              {/if}

              {#if error}
                <div class="error">
                  {error}
                </div>
              {/if}
            {/if}
          </div>


          <div class="or">
            <span>────────</span>
            <b>or</b>
            <span>────────</span>
          </div>


          <div class="action">

            <label for="dropCode">
              Enter a drop code
            </label>

            <input
              id="dropCode"
              type="text"
              placeholder="e.g. K7X2P9QM"
              bind:value={dropCode}
              maxlength="8"
            />

            <button
              class="retro-button"
              onclick={handleOpenDrop}
              disabled={opening}
            >
              {opening ? "Opening Drop..." : "📁  Open Drop"}
            </button>

          </div>

        </div>

      </section>

    </main>


    <aside class="sidebar right">

      <section class="panel">

        <div class="panel-title">
          :: info
        </div>

        <div class="info">

          <p>Fast.</p>
          <p>Simple.</p>
          <p>Anonymous.</p>
          <p>Built for everyone.</p>

          <div class="globe">
            🌐
          </div>

          <p class="quote">
            "A simpler internet<br />
            is possible."
          </p>

          <hr />

          <p>
            v1.0<br />
            zebraAFT
          </p>

        </div>

      </section>

    </aside>

  </div>

  {#if openedDrop}
  <section class="drop-view panel">

    <div class="panel-title drop-header">
  <span>:: drop {openedDrop.drop_id}</span>

  <div class="drop-header-buttons">
    <button
      class="copy-code-button"
      onclick={copyDropCode}
    >
      {codeCopied ? "✓ COPIED!" : "COPY CODE"}
    </button>

    <button
      class="copy-code-button"
      onclick={toggleQr}
    >
      {showQr ? "HIDE QR" : "SHOW QR"}
    </button>
  </div>
</div>

{#if showQr}
  <div class="qr-container">
    <img
      src={qrCodeUrl}
      alt={`QR code for Drop ${openedDrop.drop_id}`}
      class="qr-code"
    />

    <div class="qr-label">
      Scan to get Drop Code
    </div>
  </div>
{/if}

    <div class="drop-view-body">

      <div class="drop-meta">
  <div>
    <strong>Created:</strong>
    {formatDropDate(openedDrop.created_at)}
  </div>

      <div>
        <strong>Expires:</strong>
        {#if openedDrop.expires_at}
          {formatDropDate(openedDrop.expires_at)}
        {:else}
          Never
        {/if}
      </div>
    </div>

      <h2>Files in this drop</h2>
      <!-- your Add Files / Upload section -->
      <!-- your file list -->

      {#if deleteToken}
        <div class="drop-danger-zone">
          <button
            class="delete-button"
            onclick={handleDeleteDrop}
          >
            🗑 Delete this Drop
          </button>
        </div>
      {/if}

      <div class="drop-upload">
      <label class="file-picker">
        📁 &nbsp; Add Files

        <input
          type="file"
          multiple
          onchange={handleDropFiles}
        />
      </label>

      <small>
        Add more files to this drop.
      </small>


      {#if dropFiles.length > 0}

        <div class="drop-selected-files">

          <div class="selected-title">
            {dropFiles.length} file(s) selected:
          </div>

          {#each dropFiles as file}

            <div class="file-item">
              📄 {file.name}
            </div>

          {/each}

        </div>


        <button
          class="retro-button"
          onclick={handleUploadFiles}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "⬆ Upload Files"}
        </button>

        {#if uploading}
        <div class="upload-progress">

          <div class="progress-text">
            Uploading {uploadProgress} / {dropFiles.length}
          </div>

          <div class="progress-bar">
            <div
              class="progress-fill"
              style={`width: ${(uploadProgress / dropFiles.length) * 100}%`}
            ></div>
          </div>

          {#if currentUpload}
            <div class="current-upload">
              {currentUpload}
            </div>
          {/if}
        </div>
      {/if}

        {#if uploadError}
          <div class="error">
            {uploadError}
          </div>
        {/if}
      {/if}
    </div>

      {#if openedDrop.files.length === 0}

        <p class="empty-drop">
          This drop is empty.
        </p>

      {:else}

        <div class="file-list">

          {#each openedDrop.files as file}

            <div class="file-row">

  <div class="file-preview">

    {#if isImage(file.filename)}

    <img
      src={`${import.meta.env.VITE_API_URL}/files/${file.file_id}/download`}
      alt={file.filename}
    />

    {:else}

      <div class={`file-icon file-icon-${getFileType(file.filename).toLowerCase()}`}>
        {getFileType(file.filename)}
      </div>

    {/if}

  </div>


  <div class="file-info">

    <div class="file-name">
      {file.filename}
    </div>

    <div class="file-type">
      {file.filename.split(".").pop()?.toUpperCase() ?? "FILE"}
    </div>

  </div>


  <a
    class="download-button"
    href={`${import.meta.env.VITE_API_URL}/files/${file.file_id}/download`}
  >
    ↓ Download
  </a>

</div>

          {/each}

        </div>

      {/if}

    </div>

  </section>
{/if}

{#if openError}
  <div class="drop-error">
    <div class="drop-error-title">
      DROP NOT FOUND
    </div>

    <div class="drop-error-message">
      {openError}
    </div>
  </div>
{/if}

  <footer>

    <span>
      © 2025 zebraAFT
    </span>

    <span class="footer-links">
      <a href="/">privacy</a>
      |
      <a href="/">terms</a>
      |
      <a href="/">github</a>
    </span>

  </footer>

</div>