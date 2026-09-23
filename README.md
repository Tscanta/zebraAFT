# zebraAFT

### Anonymous File Transfer

zebraAFT is a lightweight, code-based file transfer application designed to move files between devices without requiring user accounts or login.

Create a Drop, upload files, share the short Drop Code, and access the files from another device.

[Live Demo](https://zebra-aft.vercel.app/) · [Backend API](https://zebraAFT-backend.onrender.com/) · [API Docs](https://zebraAFT-backend.onrender.com/docs)

---

## Screenshot

![zebraAFT home page](docs/screenshots/home.png)

---

## Features

- Anonymous file transfer without accounts
- Short 8-character Drop Codes
- Multiple file uploads
- Add files to an existing Drop
- 24-hour or permanent Drops
- Automatic expiration for temporary Drops
- Creator-only Drop deletion using a private delete token
- File downloads through the backend
- Image thumbnails
- File-type indicators for common formats
- Optional QR code display
- 100 MB maximum upload size
- Filename validation and sanitization
- Drop and file ID validation
- Expired Drop protection
- Failed-upload cleanup
- PostgreSQL persistence
- Private Supabase Storage
- Production deployment with Vercel and Render
- Environment-based API configuration

---

## How It Works

```text
Create Drop
     │
     ▼
Choose lifetime
     │
     ▼
Upload files
     │
     ▼
Receive Drop Code
     │
     ├──────────────► Share Code / QR
     │
     ▼
Open Drop from another device
     │
     ├──────────────► Download files
     │
     └──────────────► Add more files
     │
     ▼
Drop expires automatically
or the creator deletes it
```

The Drop Code is the main identifier. A separate delete token is generated for the creator and is required to delete the Drop.

---

## Architecture

![zebraAFT architecture](docs/architecture.svg)

The production system is split into four main parts:

```text
Browser
   │
   ▼
Vercel
Svelte + Vite
   │
   │ HTTPS
   ▼
Render
FastAPI + Uvicorn
   │
   ├──────────────► Supabase PostgreSQL
   │                  └── Drop + file metadata
   │
   └──────────────► Supabase Storage
                      └── Private file objects
```

### Frontend

- Svelte
- TypeScript
- Vite
- QRCode library

### Backend

- Python
- FastAPI
- Uvicorn
- psycopg2
- python-dotenv
- python-multipart
- Supabase Python client

### Infrastructure

- Vercel — frontend hosting
- Render — backend hosting
- Supabase PostgreSQL — persistent metadata
- Supabase Storage — private file storage
- GitHub — source control and deployment trigger

---

## Project Structure

```text
zebraAFT/
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── App.svelte
│   │   ├── app.css
│   │   ├── main.ts
│   │   └── lib/
│   │       └── api.ts
│   ├── index.html
│   ├── package.json
│   └── ...
│
├── docs/
│   ├── architecture.svg
│   └── screenshots/
│       └── home.png
│
├── .gitignore
└── README.md
```

---

## API

### Health Check

```http
GET /
```

Returns:

```json
{
  "message": "Anonymous File Transfer API is running"
}
```

### Create a Drop

```http
POST /drops?lifetime=24h
```

or:

```http
POST /drops?lifetime=permanent
```

Example response:

```json
{
  "drop_id": "4E439DG5",
  "delete_token": "...",
  "expires_at": "..."
}
```

### Upload a File

```http
POST /drops/{drop_id}/files
```

Uses multipart form data.

### Get a Drop

```http
GET /drops/{drop_id}
```

Returns the Drop metadata and its files.

### Download a File

```http
GET /files/{file_id}/download
```

The backend checks that the associated Drop has not expired before returning the file.

### Delete a Drop

```http
DELETE /drops/{drop_id}?delete_token=...
```

The creator's delete token is required.

---

## Database

zebraAFT uses PostgreSQL through Supabase.

### `drops`

```text
drop_id
delete_token
lifetime
created_at
expires_at
```

### `files`

```text
file_id
drop_id
filename
storage_path
created_at
```

The `files.drop_id` foreign key references `drops.drop_id` with `ON DELETE CASCADE`.

---

## Storage

Actual file bytes are stored in a private Supabase Storage bucket:

```text
uploads/
```

Storage paths use generated IDs rather than the original filename:

```text
<drop_id>/<file_id><extension>
```

The original filename is stored separately in PostgreSQL.

This allows filenames containing spaces and Unicode characters to be displayed normally without using them directly as the Storage object path.

---

## Security and Reliability

The backend includes several validation and reliability measures:

### Drop Code validation

Drop Codes must match:

```text
[A-Z0-9]{8}
```

### File ID validation

Generated file IDs are validated before download requests are processed.

### Filename validation

Uploaded filenames are:

- reduced to their basename
- stripped of surrounding whitespace
- limited to 255 characters
- rejected if they contain control characters

### Upload size limit

The current maximum is:

```text
100 MB
```

### Expiration protection

Expired Drops cannot be:

- opened
- uploaded to
- downloaded from

### Failed upload cleanup

If a file reaches Storage but its database metadata cannot be inserted, the backend attempts to remove the orphaned Storage object.

### Delete authorization

The public Drop Code is separate from the creator's private delete token.

Knowing only the Drop Code is not sufficient to perform the creator-only delete operation.

---

## Environment Variables

### Backend

Create a `.env` file for local backend development:

```env
DATABASE_URL=your_postgresql_connection_string
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

Do not commit this file.

### Frontend

For local development:

```env
VITE_API_URL=http://127.0.0.1:8000
```

For production:

```env
VITE_API_URL=https://zebraAFT-backend.onrender.com
```

The frontend `.env` file is also excluded from Git.

---

## Local Development

### Backend

From the project root:

```powershell
cd backend
```

Activate your virtual environment if you use one, then:

```powershell
uvicorn app.main:app --reload
```

The local API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server is normally available at:

```text
http://localhost:5173
```

---

## Production Deployment

### Frontend

The Svelte/Vite frontend is deployed through Vercel.

```text
https://zebra-aft.vercel.app/
```

Typical Vercel configuration:

```text
Root Directory: frontend
Framework: Vite
Build Command: npm run build
Output Directory: dist
```

Production environment variable:

```text
VITE_API_URL=https://zebraAFT-backend.onrender.com
```

### Backend

The FastAPI backend is deployed through Render.

```text
https://zebraAFT-backend.onrender.com
```

Render configuration:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required Render environment variables:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

---

## Git Workflow

The project uses GitHub as the source repository.

A normal development cycle is:

```text
Edit
  ↓
Test locally
  ↓
git add .
  ↓
git commit
  ↓
git push origin main
```

Vercel and Render are connected to the GitHub repository, so pushes to the configured branch can trigger deployments automatically.

---

## Screenshots for the README

The README currently includes the home-page screenshot.

For a stronger GitHub presentation, I recommend adding these **three actual screenshots**:

### 1. Home page

File:

```text
docs/screenshots/home.png
```

Place it directly below the title or in the `Screenshot` section.

Show:

- zebraAFT logo
- file picker
- Drop creation controls

### 2. Active Drop

File:

```text
docs/screenshots/drop.png
```

Take this after creating a Drop.

Try to capture:

- Drop Code
- Copy Code button
- Show QR button
- expiration information
- uploaded files
- download buttons

Add it below the `How It Works` section:

```markdown
## Drop Interface

![Active Drop](docs/screenshots/drop.png)
```

### 3. Mobile / Second Device

File:

```text
docs/screenshots/mobile.png
```

Show the same Drop being opened from a phone or another browser.

This demonstrates the actual purpose of the project better than another desktop screenshot.

Add:

```markdown
## Cross-Device Transfer

![Cross-device transfer](docs/screenshots/mobile.png)
```

### Optional 4. QR Code

File:

```text
docs/screenshots/qr.png
```

Show the Drop page with the QR code visible.

This is optional because the Drop screenshot can already show the QR.

---

## Recommended README Screenshot Layout

A clean GitHub README could look like:

```text
zebraAFT
Anonymous File Transfer

[Live Demo] [API Docs]

              HOME SCREENSHOT

About
Features
How It Works

              ACTIVE DROP SCREENSHOT

Architecture
Tech Stack
API
Database
Storage
Security
Local Development
Production Deployment
```

I would **not** add lots of screenshots. Three strong screenshots are enough.

---

# 📄 LICENSE

This project is licensed under the MIT License.
