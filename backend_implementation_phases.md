# Backend Implementation Roadmap
**Project: Internship Portal**
**Stack: FastAPI (Python) + Supabase**

This roadmap details the sequential execution phases to build the FastAPI network routing layer interconnected with a live Supabase ecosystem.

---

## Phase 1: Environment & Supabase Configuration
**Goal:** Initialize the FastAPI project, hook up the Supabase Client SDK, and provision the Postgres remote definitions.

*   **1.1 Project Initialization:** Scaffold the FastAPI project structure. Generate the `.env` handling to securely inject `SUPABASE_URL` and `SUPABASE_KEY`.
*   **1.2 Supabase SDK Integration:** Install the `supabase` Python library. Instantiate a global client session inside the core `database.py` file to communicate with the DB layer seamlessly.
*   **1.3 Remote Database Modeling:** Build the schema explicitly inside the Supabase SQL Editor. Execute table generation corresponding to `Profiles`, `Assignments`, `Submissions`, and `Attendance`.
*   **1.4 Row Level Security (RLS) Setup:** Configure strict RLS Postgres policies directly inside the Supabase dashboard guaranteeing zero unauthorized entity manipulations.

## Phase 2: Authentication Handshake
**Goal:** Hook FastAPI endpoints securely into Supabase Auth processes.

*   **2.1 Auth Controllers:** Implement `POST /api/auth/register` and `POST /api/auth/login`. Have the FastAPI logic route the provided email/passwords into `supabase.auth.sign_up()` and trap/format the error messages seamlessly.
*   **2.2 Postgres Triggers:** Create a remote SQL trigger that automatically inserts a generated user record into the public `Profiles` table any time a student registers inside the protected `auth.users` schema.
*   **2.3 JWT Injection:** Configure a FastAPI `Depends` authentication middleware that decodes and validates the `Bearer` token natively attached to subsequent frontend requests, isolating the `user_id` context natively.

## Phase 3: Profile & Core Assignments
**Goal:** Build the CRUD layer dictating internal curriculum structure.

*   **3.1 Profile Linking:** Write `GET` and `PUT` methods for `/api/users/profile` utilizing `supabase.table('Profiles').select(...).eq('id', user_id)`.
*   **3.2 Assignment Broadcasting:** Implement `POST /api/assignments`. Fast API decodes the payload, validates the variables via Pydantic, and calls `.insert()` natively against Supabase.
*   **3.3 Data Retrieval:** Build `GET /api/assignments`. Apply necessary `.order()` and `.limit()` filter parameters to output JSON streams to the frontend efficiently dynamically context-aware based on the user's Role.

## Phase 4: Submissions & Grading Engine
**Goal:** Let candidates upload assets linking them hierarchically natively onto assignments.

*   **4.1 Submissions Controller:** Build `POST /api/submissions`. The FastAPI controller executes datetime math locking in the `status` string (On-Time versus Late) before hitting `.insert()`.
*   **4.2 Grading Execution:** Develop `PUT /api/submissions/{id}/grade` exposing `supabase.table().update()` queries constrained directly to authenticated Teachers routing evaluation values.

## Phase 5: Attendance Module
**Goal:** Integrate heavy bulk-row ingestion dynamically natively supported via API parameters.

*   **5.1 Batch Querying:** Map the frontend attendance arrays inside `POST /api/attendance` converting them into `.insert([list_of_dictionaries])` executing a solitary network burst against Supabase improving latencies cleanly.
*   **5.2 Dashboard Calculation:** Map `GET /api/attendance/summary`.

## Phase 6: Analytics & Dashboard Finalization
**Goal:** Generate KPI visualizations natively via the routing configurations.

*   **6.1 System Dashboards:** Write `GET /api/analytics/dashboard`. Leverage the Supabase `{count='exact'}` wrapper alongside complex `.select()` methodologies to aggregate numbers without downloading heavy datasets into Python memory.
*   **6.2 Documentation Finalization:** Generate the Swagger UI (automatically handled securely by FastAPI `<host>/docs`) to provide granular functional testing surfaces.

## Phase 7: Reflex UI Integration
**Goal:** Interconnect the front-facing user screens cleanly up onto the APIs securely generated above.

*   **7.1 Network Transport Methods:** Replace dummy JSON variables inside the Reflex `state.py` mechanisms utilizing `httpx` to strictly route network packages referencing `http://127.0.0.1:8000/api/...` endpoint URLs directly.
*   **7.2 State Callbacks:** Structure Error Handling securely utilizing `.json()["detail"]` responses emitted out natively from FastAPI triggering `rx.toast.error` elegantly.
