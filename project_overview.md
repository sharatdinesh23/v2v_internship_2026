# Internship Portal: Technical Overview

This document provides a high-level and detailed architectural overview of the **Internship Portal** project, covering both the **FastAPI Backend** and the **Reflex Frontend**.

---

## 🏗️ Architecture Overview

The system follows a classic **Client-Server** architecture with three primary layers:
1.  **Backend (FastAPI)**: A high-performance REST API handling business logic, authentication, and database interactions.
2.  **Frontend (Reflex)**: A reactive web application built entirely in Python, utilizing `httpx` for asynchronous communication with the backend.
3.  **Database (Supabase/PostgreSQL)**: A managed PostgreSQL database for data persistence and authentication.

---

## 🔙 Backend (FastAPI)

Located in the `/Backend` directory, the backend provides the engine for the entire platform.

### Key Components:
-   **`app.py`**: The entry point. Configures CORS (allowing `localhost:3000`), error handling, and router inclusion.
-   **`auth.py`**: Implements JWT (JSON Web Token) authentication. It queries the `Profiles` table to resolve user roles (`student`, `teacher`, `admin`) and associated `internship_id`.
-   **Routers**:
    -   `/api/auth/`: Login and token generation.
    -   `/api/assignments/`: CRUD for assignments.
    -   `/api/submissions/`: File upload metadata and grading logic.
    -   `/api/internships/`: Admin-level program management.
-   **Schemas (`schemas/core.py`)**: Pydantic models for request validation and response serialization.

### Security:
-   **JWT-Based**: Every protected request requires an `Authorization: Bearer <token>` header.
-   **Role-Based Access Control (RBAC)**: Endpoints verify the `role` claim in the JWT to restrict access to admin or teacher specific features.

---

## 🎨 Frontend (Reflex)

Located in `/internship_portal`, the frontend is a modern, reactive single-page application (SPA).

### State Management (`state.py`):
-   **`AppState`**: The central source of truth. It manages:
    -   User session (`auth_token`, `is_logged_in`).
    -   Reactive metrics (KPIs for dashboards).
    -   Modal states (Login, Creation, Review).
    -   Asynchronous API calls via `httpx`.

### Page Structure:
1.  **Login (`pages/login.py`)**: Authenticates users and routes them to the appropriate dashboard.
2.  **Dashboards**:
    -   **Student**: Viewing assignments and submitting work.
    -   **Teacher**: Reviewing student submissions and managing deadlines.
    -   **Admin**: High-level analytics, program management, and teacher assignment.
3.  **Settings (`pages/settings.py`)**: Profile management and password updates.

### Design System (`styles.py` & `components.py`):
-   **Indigo Nocturne Theme**: Customizable color tokens for a premium, dark-mode aesthetic.
-   **Shared Components**: Sidebar, Page Header, and KPI Cards are extracted for consistency across all roles.

---

## 🔄 Integration Workflow

1.  **Authentication**: User logs in -> Frontend saves JWT as an `rx.Cookie` -> `AppState` populates user role and ID.
2.  **Data Fetching**: Pages use `on_mount` hooks to trigger `AppState.fetch_...()` methods. These methods perform `client.get()` calls to the FastAPI backend (Port 8888).
3.  **Reactive UI**: Upon receiving API data, `AppState` attributes are updated. Reflex automatically re-renders the UI components bound to these attributes.

---

## 🚀 Environment Configuration

-   **Backend Port**: `8888` (Uvicorn running on Windows).
-   **Frontend Port**: `3000` (Node.js/Next.js wrapper).
-   **Database**: Supabase URL and Key are managed via repository secrets or `.env` files.

---

## 🛠️ Key Features
-   **Soft Delete**: Internships are deactivated (`is_active=False`) rather than purged from the database.
-   **Multi-Role Dashboards**: A unified codebase that serves three distinct user experiences based on role.
-   **Real-time Analytics**: Admin and Teacher dashboards provide live counts of pending reviews and on-time submissions.
