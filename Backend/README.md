# Public Services Backend API

Backend API cho ứng dụng Dịch vụ công số với hệ thống xác thực JWT và phân quyền.

## Cài đặt

1. Cài đặt dependencies:
```bash
npm install
```

2. Tạo file `.env` (đã có sẵn template):
```env
PORT=8888
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
NODE_ENV=development
```

3. Chạy server:
```bash
npm run dev
```

Hoặc sử dụng file `start-server.bat` trên Windows.

## API Endpoints

### Authentication

# Public Services Backend

This folder contains two possible backend implementations for the demo Public Services application:

- Original Node.js/Express implementation (legacy, kept for compatibility)
- New Python/Flask implementation (migration in-progress)

This README documents how to run either implementation, how to seed demo data, and important runtime notes.

---

## Quick Start — Node (existing)

1. Install Node dependencies:

```powershell
cd "c:\\Users\\ADMIN\\Downloads\\E-Map\\Backend"
npm install
```

2. Create `.env` (example):

```text
PORT=8888
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
NODE_ENV=development
```

3. Start dev server (uses `nodemon`):

```powershell
npm run dev
```

Or run once:

```powershell
npm start
```

To seed demo data with the Node script (if you still have the Node scripts):

```powershell
npm run seed
```

---

## Quick Start — Python/Flask (recommended for migration)

1. Create and activate a virtual environment, then install minimal deps:

```powershell
cd "c:\\Users\\ADMIN\\Downloads\\E-Map\\Backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# if requirements.txt is missing, at minimum install:
pip install flask flask-cors pyjwt
```

2. Run the Flask server:

```powershell
python server.py
```

The Python routes mirror the original Express routes and are located in `routes/*.py`.

---

## Seeding demo data

- Python seed script: `python scripts/seed_data.py` (creates categories and sample public services).
- Node seed script (legacy): `npm run seed` (if present).

---

## Important behavior notes

- Submitting an application requires at least 1 uploaded file/photo. The API will return 400 if no files are included on create.
- Multipart form field name for files is `files` (multiple allowed).
- Uploaded files are stored under `Backend/uploads/` (local file storage used for demo).
- Document processing is a light-weight placeholder: only `.txt` files are read for text extraction by default. Integrate OCR libraries (`pytesseract`, `pdfminer.six`, `PyMuPDF`) to extract text from images/PDFs.

---

## Environment variables

- `PORT` — HTTP port (default 8888)
- `JWT_SECRET` — Secret used to sign JWTs (change for production)
- `JWT_EXPIRES_IN` — Token expiry (e.g. `7d`)
- `NODE_ENV` / `FLASK_ENV` — environment

---

## Where to look next

- Python routes: `routes/*.py`
- Python models: `models/*.py` (file-based JSON storage in `data/`)
- Document processor: `services/document_processor.py` (current placeholder)

If you want, I can:

- Add OCR/PDF extraction to `services/document_processor.py` and update `requirements.txt`.
- Create a `requirements.txt` with pinned versions.
- Commit the Python migration and remove legacy Node start scripts.

---

If anything should be adjusted for your preferred workflow (Node vs Python), tell me which and I will update the README and scripts accordingly.

