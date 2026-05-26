# 🚀 Deployment Guide: Internship Portal

This guide explains how to deploy the **FastAPI Backend** and **Reflex Frontend** to production using **Render** and **Vercel**.

---

## 🏗️ Phase 1: Prepare Your Repository

Ensure your project structure is clean and all sensitive keys are in `.env` (which should be in `.gitignore`).

1.  **Backend Directory**: `/Backend`
2.  **Frontend Directory**: `/internship_portal`

---

## 🔙 Phase 2: Deploying the Backend (Render)

Render is ideal for Python APIs.

### 1. Create a Web Service
-   Connect your GitHub repository.
-   Select the **`Backend`** directory as the root.
-   **Environment**: `Python 3`
-   **Build Command**: `pip install -r requirements.txt`
-   **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 10000`

### 2. Configure Environment Variables
In the Render Dashboard, add:
-   `SUPABASE_URL`: `https://your-project.supabase.co`
-   `SUPABASE_KEY`: `your-anon-or-service-role-key`
-   `ALLOWED_ORIGIN`: `https://your-frontend-domain.vercel.app` (Add this *after* deploying frontend)

---

## 🎨 Phase 3: Deploying the Frontend (Reflex)

Reflex can be deployed as a static site (frontend) + a separate backend process, or as a full-stack container.

### Option A: Vercel (Frontend Only)
Vercel is best for the static part of Reflex.

1.  **Export the App**:
    In your local `/internship_portal` directory, run:
    ```bash
    reflex export --frontend-only
    ```
    This generates a `.vercel` or `out` directory.
2.  **Deploy**:
    Push the exported code or use the Vercel CLI.
    -   **Build Command**: `reflex export --frontend-only`
    -   **Output Directory**: `.web/_static`
3.  **Environment Variables**:
    -   `API_URL`: `https://your-backend-on-render.onrender.com`

### Option B: Render (Full Stack with Docker)
If you want to keep everything on Render, use a **Dockerfile**.

1.  **Create a `Dockerfile`** in the root:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY . .
    RUN pip install -r requirements.txt
    RUN reflex init
    CMD ["reflex", "run", "--env", "prod"]
    ```
2.  **Connect to Render** as a **Web Service**.
3.  **Environment**: `Docker`

---

## 🔄 Phase 4: Connecting the Dots

Once both are live, update your URLs:

1.  **Backend CORS**: Update `ALLOWED_ORIGIN` in Render to match your Vercel URL.
2.  **Frontend API**: Update the `api_url` in your Reflex `AppState` (or via environment variable) to point to the Render Backend URL.

---

## 📝 Common Deployment Checklist

- [ ] **Supabase Roles**: Ensure your `SUPABASE_SERVICE_ROLE_KEY` is set in the production environment for teacher creation to work.
- [ ] **SSL**: Ensure you are using `https://` for all API calls in production.
- [ ] **Database Migrations**: Run any necessary SQL scripts in the Supabase Dashboard before the first deployment.
- [ ] **Ports**: Render uses port `10000` by default; ensure your `uvicorn` command respects this.

---

## 🛠️ Troubleshooting
- **CORS Errors**: Usually means the Backend `ALLOWED_ORIGIN` doesn't exactly match the Frontend URL (including trailing slashes).
- **Reflex Build Failure**: Ensure `npm` is available in the build environment as Reflex uses it for the frontend compilation.
