# Praeventix EWS: Deployment Guide (Vercel & Render)

This guide outlines the steps to deploy the full-stack Praeventix EWS platform.

## 🏗️ Architecture Overview
*   **Frontend**: Next.js 14+ (Deployed on **Vercel**)
*   **Backend**: BentoML / FastAPI (Deployed on **Render**)
*   **Database**: SQLite (Local for this demo; persistent disk required for production)

---

## 1. Backend Deployment (Render)

### Step 1: Create requirements.txt
I have already generated `backend/requirements.txt`. Ensure this is committed to your repository.

### Step 2: Configure Render Web Service
1.  Log in to [Render](https://render.com).
2.  Click **New +** > **Web Service**.
3.  Connect your GitHub repository.
4.  **Settings**:
    *   **Name**: `praeventix-backend`
    *   **Root Directory**: `backend`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `python -m bentoml serve service:BankRiskService --port $PORT`

### Step 3: Environment Variables
Add the following in the Render **Environment** tab:
*   `GEMINI_API_KEY`: Your Google Gemini API Key.
*   `OPENROUTER_API_KEY`: (Optional) For LLM failover.

### Step 4: Persistent Disk (Required for SQLite)
Since SQLite is file-based, Render will wipe data on every restart.
1.  Go to the **Disks** tab in your Render service.
2.  Add a disk (e.g., 1GB).
3.  Mount Path: `/opt/render/project/src/backend/data`
4.  Update your `.env` or `setup_db.py` to point the DB to this path.

---

## 2. Frontend Deployment (Vercel)

### Step 1: Configure Environment Variables
1.  Log in to [Vercel](https://vercel.com).
2.  Import your repository.
3.  In the **Environment Variables** section, add:
    *   `NEXT_PUBLIC_BACKEND_URL`: The URL of your Render backend (e.g., `https://praeventix-backend.onrender.com`).

### Step 2: Build & Deploy
Vercel will automatically detect the Next.js framework.
*   **Framework Preset**: `Next.js`
*   **Root Directory**: `./` (Root of the repo)

### Step 3: Verify Rewrites
Your `next.config.mjs` is already pre-configured to handle API rewrites:
```javascript
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';
// This ensures that /api/ml/* calls are routed to your Render backend.
```

---

## 3. High-Fidelity Sync (Post-Deployment)
Once deployed, run the initialization command via a terminal or a one-time script:
1.  **Seed Data**: Ensure the database is seeded by running `setup_db.py`.
2.  **Train Models**: Run `train_from_db.py` to ensure BentoML has local models ready to serve.

---
*Praeventix Platinum: Enterprise Intelligence, Anywhere.*
