# Anonymous File Transfer

A lightweight file-transfer web application that lets users share files between devices using a short **drop code**, without requiring an account or login.

> **Status:** 🚧 In Development

## ✨ Overview

Anonymous File Transfer is designed for quickly moving files between devices, especially when using a public or shared computer.

Instead of creating an account or sending a traditional share link, a user can:

1. Select one or more files.
2. Create a temporary drop.
3. Receive a short drop code.
4. Enter that code on another device.
5. View and download the files.

The project is being built with a simple frontend/backend architecture and Supabase for persistent cloud data.

---

## 🖥️ How It Works

```text
                 DEVICE A
                    │
                    │ Select files
                    ▼
             ┌──────────────┐
             │ Create Drop  │
             └──────┬───────┘
                    │
                    ▼
              KOUH3XG3
                    │
                    │ Enter code
                    ▼
                 DEVICE B
                    │
                    ▼
             ┌──────────────┐
             │  Load Drop   │
             └──────┬───────┘
                    │
                    ▼
              Download Files
```

Each drop has a unique code that can be used to retrieve the files.

---

## 🚀 Features

### Current / Implemented

- 📁 Multiple file selection
- ☁️ Supabase integration
- 🔑 Short randomly generated drop codes
- ⏱️ Drop lifetime selection
- 🗑️ Drop deletion
- 📥 File retrieval/download flow
- 🖥️ Responsive web interface
- ⚡ Svelte + Vite frontend
- 🚀 FastAPI backend
- 🗄️ PostgreSQL/Supabase database

### In Development

- 📱 QR-code sharing
- 🔳 Show QR button on demand
- 🧹 Reliable automatic cleanup of expired drops/files
- 🖼️ Improved file thumbnails/previews
- 🔐 Better validation and error handling
- 🌐 Production deployment

---

## 🛠️ Tech Stack

### Frontend

- [Svelte](https://svelte.dev/)
- [Vite](https://vitejs.dev/)
- TypeScript
- HTML/CSS
- `qrcode` for QR-code generation

### Backend

- Python
- [FastAPI](https://fastapi.tiangolo.com/)
- Uvicorn
- REST API

### Database & Storage

- [Supabase](https://supabase.com/)
- PostgreSQL
- Supabase Storage

---

## 📂 Project Structure

```text
anonymous-file-transfer/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   ├── uploads/
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── lib/
│   │   │   └── api.ts
│   │   ├── App.svelte
│   │   ├── app.css
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── ...
│
├── .gitignore
└── README.md
```

> The structure may change as the project develops.

---

## ⚙️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/anonymous-file-transfer.git
cd anonymous-file-transfer
```

---

# Backend Setup

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create a `.env` file for the backend.

Example:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=your_database_connection_string
```

**Never commit real credentials to GitHub.**

Make sure `.env` is included in `.gitignore`.

### 5. Start FastAPI

From the backend/project directory, run the command appropriate to your project structure, for example:

```bash
uvicorn app.main:app --reload
```

The API should then be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

### 6. Install frontend dependencies

```bash
cd frontend
npm install
```

If QR functionality is enabled:

```bash
npm install qrcode
npm install -D @types/qrcode
```

### 7. Start the frontend

```bash
npm run dev
```

Vite will normally provide:

```text
http://localhost:5173
```

---

## 🔄 Example Workflow

### Device A

```text
1. Open the application
2. Select files
3. Choose drop lifetime
4. Create the drop
5. Receive a drop code
6. Share the code / QR code
```

Example:

```text
KOUH3XG3
```

### Device B

```text
1. Open the application
2. Enter KOUH3XG3
3. Load the drop
4. View available files
5. Download the required files
```

No account is required for the transfer flow.

---

## ⏱️ Drop Expiration

Drops can be configured with a lifetime such as:

```text
24 hours
```

Expired drops should be removed automatically so that old files do not remain indefinitely.

The cleanup system is still being refined to ensure that both:

- database records
- stored files

are removed correctly.

---

## 🔐 Security Considerations

This project is designed around anonymous file sharing, but anonymity does **not** automatically mean complete privacy or security.

Before production deployment, the following areas need to be addressed carefully:

- File-size limits
- Allowed file types
- Rate limiting
- Abuse prevention
- Expiration enforcement
- Secure Supabase Storage policies
- Random/unpredictable drop IDs
- HTTPS
- Server-side validation
- Download authorization
- Storage cleanup
- Protection against malicious uploads

Do not treat the current development version as a hardened production file-sharing service.

---

## 🗺️ Roadmap

### Phase 1 — Core Transfer

- [x] File selection
- [x] Create drops
- [x] Generate drop codes
- [x] Upload files
- [x] Retrieve drops
- [x] Download files
- [x] Drop deletion

### Phase 2 — User Experience

- [x] Svelte frontend
- [x] File previews
- [ ] Better thumbnails for non-image files
- [ ] Improved loading states
- [ ] Better error messages
- [ ] Mobile UI improvements
- [ ] QR sharing

### Phase 3 — Storage

- [x] Supabase database integration
- [x] Supabase Storage integration
- [ ] Automatic expired-file deletion
- [ ] Storage cleanup verification
- [ ] Storage usage limits

### Phase 4 — Production

- [ ] Deploy frontend
- [ ] Deploy FastAPI backend
- [ ] Configure production CORS
- [ ] HTTPS
- [ ] Rate limiting
- [ ] File-size restrictions
- [ ] Abuse protection
- [ ] Production Supabase policies
- [ ] Monitoring/logging

---

## 🧪 Development

Frontend:

```bash
cd frontend
npm run dev
```

Backend:

```bash
uvicorn app.main:app --reload
```

Check API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-feature
```

3. Make your changes.
4. Test them locally.
5. Commit your changes.

```bash
git add .
git commit -m "feat: add my feature"
```

6. Push the branch.

```bash
git push origin feature/my-feature
```

7. Open a Pull Request.

---

## 📜 License

Add your preferred license here.

For example:

```text
MIT License
```

---

## 👤 Author

**Tshedup**

Built as a personal software project focused on simple, anonymous device-to-device file transfer.

---

## ⭐ Project Goal

The long-term goal is to make file transfer feel as simple as:

```text
Select → Create Drop → Share Code → Download
```

No account.

No complicated setup.

Just the files you need, when you need them.
