# Backend API & System Architecture Design
**Project: Internship Portal (Role-Based)**
**Stack: FastAPI (Python) + Supabase**

This document outlines the Low-Level Design (LLD), functional endpoints, payload structures, and security considerations required to construct the backend for the Internship Portal utilizing **FastAPI** as the routing interface and **Supabase** (PostgreSQL, Auth, Storage) as the Database and Authentication provider.

---

## 1. Low-Level Design (LLD) Perspective

The backend logic acts as a 3-tier bridge wrapping the Supabase ecosystem:

*   **Controller Layer (FastAPI Routers):** Responsible strictly for receiving HTTP requests from the Reflex frontend, validating incoming JSON payloads via Pydantic, and calling the Service method.
*   **Service Layer (Business Logic):** Validates logical conditions (e.g. submission deadline checks) and prepares the data.
*   **Repository Layer (Supabase Client):** Acts as the ORM. Uses the `supabase-py` client library to natively execute operations (`supabase.table('...').select()`) directly against the Supabase PostgreSQL database.

### Database Entities / Tables (Supabase Schema)

*Note: The primary User credential tracking is handled natively by Supabase's `auth.users` mapping.*

1. **Internships** (Master table defining the available programs)
   * `id`: **UUID** (Primary Key)
   * `name`: **VARCHAR(255)** (e.g., 'Web Dev Beta')
   * `description`: **TEXT**
   * `status`: **ENUM** ('Active', 'Upcoming', 'Completed')
   * `created_at`: **TIMESTAMP** (Default: CURRENT_TIMESTAMP)

2. **Profiles** (Extends Supabase `auth.users` for platform-specific roles)
   * `id`: **UUID** (Primary Key, Foreign Key -> `auth.users.id`)
   * `name`: **VARCHAR(255)**
   * `email`: **VARCHAR(255)** (Unique)
   * `role`: **ENUM** ('student', 'teacher', 'admin')
   * `created_at`: **TIMESTAMP** (Default: CURRENT_TIMESTAMP)

3. **Internship_Participants** (Maps Students and Teachers to specific Internships)
   * `id`: **UUID** (Primary Key)
   * `internship_id`: **UUID** (Foreign Key referencing Internships.id)
   * `user_id`: **UUID** (Foreign Key referencing Profiles.id)
   * `joined_at`: **TIMESTAMP** (Default: CURRENT_TIMESTAMP)

4. **Assignments** 
   * `id`: **UUID** (Primary Key)
   * `internship_id`: **UUID** (Foreign Key referencing Internships.id)
   * `title`: **VARCHAR(255)**
   * `description`: **TEXT**
   * `doc_link`: **VARCHAR(512)** (Nullable)
   * `due_date`: **TIMESTAMP**
   * `created_by`: **UUID** (Foreign Key referencing Profiles.id)
   * `created_at`: **TIMESTAMP** (Default: CURRENT_TIMESTAMP)

5. **Submissions** 
   * `id`: **UUID** (Primary Key)
   * `assignment_id`: **UUID** (Foreign Key referencing Assignments.id)
   * `student_id`: **UUID** (Foreign Key referencing Profiles.id)
   * `repo_link`: **VARCHAR(512)**
   * `status`: **ENUM** ('Pending', 'Graded', 'Late')
   * `grade`: **VARCHAR(50)** (Nullable string representation, e.g., 'A')
   * `submitted_at`: **TIMESTAMP** (Default: CURRENT_TIMESTAMP)

6. **Attendance** 
   * `id`: **UUID** (Primary Key)
   * `student_id`: **UUID** (Foreign Key referencing Profiles.id)
   * `date`: **DATE**
   * `status`: **ENUM** ('Present', 'Absent', 'Late')
   * `recorded_by`: **UUID** (Foreign Key referencing Profiles.id)

---

## 2. API Endpoints

### A. Authentication & User Management (Supabase Wrapped)
*   **`POST /api/auth/login`**
    *   **Description:** Authenticates user via `supabase.auth.sign_in_with_password()`.
    *   **Payload:** `{ "email": "student@gmail.com", "password": "password123" }`
    *   **Returns:** `{ "access_token": "ey...", "user": { "id": "uuid", "role": "student" } }`

*   **`POST /api/auth/register`**
    *   **Description:** Registers a new user via `supabase.auth.sign_up()`. Triggers a database webhook to auto-insert a row into the `Profiles` table mapping the `auth.users.id`.
    *   **Payload:** `{ "full_name": "...", "email": "...", "password": "...", "role": "student" }`
    *   **Returns:** `{ "message": "User registered successfully", "user_id": 1 }`

*   **`GET /api/users/profile`**
    *   **Description:** Retrieves `Profiles` data based on the securely parsed Supabase JWT.
    *   **Returns:** `{ "id": "uuid", "name": "Rahul Sharma", "email": "...", "department": "IT", ... }`

### B. Assignment Management
*   **`GET /api/assignments`**
    *   **Description:** Uses `supabase.table('Assignments').select('*')` to pull active assignments. 
    *   **Returns:** `[ { "id": "uuid", "title": "Web Dev Project", "due_date": "2026-04-15", ... } ]`

*   **`POST /api/assignments`**
    *   **Description:** Inserts a new assignment into the Supabase table.
    *   **RBAC:** Teachers & Admins ONLY.
    *   **Payload:** `{ "title": "React Lab", "description": "...", "doc_link": "https://drive...", "due_date": "2026-04-20" }`

### C. Submissions & Grading
*   **`POST /api/submissions`**
    *   **Description:** Student submits their assignment code link. Backend calculates whether "On Time" or "Late" compared to the `due_date`.
    *   **RBAC:** Students ONLY.
    *   **Payload:** `{ "assignment_id": "uuid", "repo_link": "https://github.com/..." }`

*   **`PUT /api/submissions/{submission_id}/grade`**
    *   **Description:** Allows Teachers to execute a Supabase `update()` marking the grade fields.
    *   **RBAC:** Teachers & Admins ONLY.
    *   **Payload:** `{ "grade": "A", "feedback": "Great implementation." }`

### D. Attendance Management
*   **`POST /api/attendance`**
    *   **Description:** Batch inserts new Attendance rows into Supabase.
    *   **RBAC:** Teachers & Admins ONLY.
    *   **Payload:** `{ "date": "2026-03-25", "records": [ {"student_id": "uuid", "status": "Present"} ] }`

### E. Analytics / Dashboards
*   **`GET /api/analytics/dashboard`**
    *   **Description:** Executes optimized count queries via the Supabase client (`.select('*', count='exact')`) to generate total metrics.
    *   **Returns:** `{ "total_assignments": 60, "total_students": 400, "total_submissions": 1200, "on_time_count": 1080 }`

---

## 3. Security Measures

1.  **Delegated Authentication:** We do not write custom password hashing (Bcrypt) logic. Supabase natively encrypts user credentials inside `auth.users`.
2.  **Row Level Security (RLS):** Supabase RLS policies will be enforced on the PostgreSQL level. This means even if the API layer makes a mistake, the database physically rejects queries (e.g., stopping a student from generating an Assignment row) if the associated JWT `role` is incapable.
3.  **FastAPI Dependency Injection:** Fast API endpoints use `Depends(get_current_user)` to cryptographically verify the Supabase JWT Bearer token natively on every secure route.
4.  **Pydantic Schema Validation:** FastAPI explicitly uses Pydantic object models to reject malformed payload boundaries automatically before the logic ever hits the Supabase network client.
5.  **CORS Headers:** explicitly lock the FastAPI middleware to only accept HTTP requests originating from the frontend Reflex host.
