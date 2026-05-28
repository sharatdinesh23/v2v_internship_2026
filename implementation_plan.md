# AWS Free Tier Deployment Plan: Internship Portal

This plan outlines how to host both the **FastAPI Backend** and the **Reflex Frontend/Backend event server** on the **AWS Free Tier (12-Month Free EC2 `t2.micro` or `t3.micro` instance)**, while keeping your database on **Supabase**.

---

## 📐 Architecture Overview

To stay strictly within the AWS Free Tier, we will consolidate the entire application stack onto a single EC2 instance using **Docker Compose** and **Nginx**. This provides a production-grade, highly cost-effective, and fully isolated environment.

```mermaid
graph TD
    Client[Web Browser] -- HTTPS (443) / WSS --> Nginx[Nginx Reverse Proxy & Static Host]
    Nginx -- Serves Static Content --> Client
    Nginx -- API Requests (/api/*) --> FastAPI[FastAPI Backend (Port 8888)]
    Nginx -- Websocket / UI State (/_event/*) --> ReflexBE[Reflex Backend Event Server (Port 8010)]
    FastAPI -- Data Operations --> Supabase[(Supabase Database & Auth)]
    ReflexBE -- API calls --> FastAPI
```

### Why a Single EC2 Instance?
1. **100% Free**: Under the AWS Free Tier, new accounts get **750 hours/month** of a `t2.micro` or `t3.micro` Linux instance free for 12 months. This is exactly enough to run 24/7.
2. **Simplified Networking**: Hosting FastAPI, the Reflex event server, and Nginx on the same machine avoids cross-network latency, VPC peering, and NAT Gateway charges (which are NOT free).
3. **SSL/TLS & Reverse Proxying**: Nginx acts as our single entry point. It serves the statically compiled Reflex frontend directly from disk, reverse-proxies APIs to the FastAPI backend, handles WebSocket upgrades for Reflex's UI state, and uses **Certbot** for **100% free auto-renewing SSL certificates** from Let's Encrypt.

---

## 📌 User Review Required

Please review the following requirements and recommendations before giving approval:

> [!IMPORTANT]
> **Domain Name Requirement**
> To set up SSL (HTTPS/WSS) in production, you will need a domain name (e.g. `portal.v2vclasses.com`). If you don't want to buy one, you can use a free dynamic DNS provider like **DuckDNS** (e.g., `v2v-portal.duckdns.org`), which is completely free and works perfectly with Let's Encrypt!

> [!TIP]
> **Supabase Configuration**
> Your database will remain entirely hosted on **Supabase**. You will need your Supabase Project URL, Anon Key, and Service Role Key (already present in your `.env` file) to configure the backend on EC2.

---

## 🛠️ Proposed Changes

We will introduce Docker files, deployment scripts, and modify a few hardcoded localhost references to support dynamic runtime environment variables.

### 🌐 Frontend & Config Adjustments

#### [MODIFY] [rxconfig.py](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/internship_portal/rxconfig.py)
*   Update `api_url` in the Reflex configuration to read from an environment variable (`REFLEX_API_URL`), falling back to local port 8010. This ensures Reflex compiles the static JS pointing to your custom domain in production.

#### [MODIFY] [state.py](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/internship_portal/internship_portal/state.py)
*   Modify `api_url` inside `AppState` to dynamically load `FASTAPI_API_URL` from environment variables, falling back to local port `8888`. This allows the Reflex event server to route requests to the FastAPI backend in production.

#### [MODIFY] [logger.py](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/internship_portal/internship_portal/logger.py)
*   Modify `API_URL` to load `FASTAPI_API_URL` from environment variables, ensuring that frontend log streaming matches your production backend API.

---

### 📦 New Containerization & Orchestration Files

#### [NEW] [Dockerfile](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/Backend/Dockerfile)
*   Create a Dockerfile for the FastAPI backend using `python:3.11-slim` to minimize image size.

#### [NEW] [Dockerfile](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/internship_portal/Dockerfile)
*   Create a Dockerfile for the Reflex Application. It will:
    1. Base off `python:3.11-slim`.
    2. Install `nodejs` and `npm` (required by Reflex to compile the frontend).
    3. Install python dependencies.
    4. Initialize and compile the Reflex app.
    5. Run the Reflex backend event server in production mode.

#### [NEW] [docker-compose.yml](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/docker-compose.yml)
*   Define a multi-container architecture in the root:
    *   `backend`: FastAPI API server on port 8888.
    *   `reflex-backend`: Reflex State Event Server on port 8010.
    *   `nginx`: Port 80/443 mapping, proxying traffic, serving compiled static assets directly from a shared volume.

#### [NEW] [nginx.conf](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/nginx.conf)
*   Create a production Nginx configuration supporting:
    *   Static files rendering.
    *   `client_max_body_size 20M` (to handle Excel/bulk uploads smoothly).
    *   WebSocket upgrade directives (required for Reflex's live state engine).
    *   Forwarding `/api` requests to the FastAPI backend.

#### [NEW] [deploy.sh](file:///c:/Users/shara/OneDrive/Desktop/my_Folder/V2VClasses/Internship/Internship%20-%202026/Internship%20Portal/Antigravity%20UI/deploy.sh)
*   A premium, automated bash script to execute on the EC2 instance. It will:
    *   Install system prerequisites (Docker, Git).
    *   Create directories and request user input for Environment keys (Supabase details, Custom Domain).
    *   Automatically spin up the containerized stack.
    *   Integrate Certbot to set up SSL with zero friction.

---

## 🧪 Verification Plan

### Manual Verification Instructions (on EC2)
1. **EC2 Provisioning**: Set up a `t2.micro` or `t3.micro` instance in AWS with Ubuntu 24.04 LTS. Open port 80, 443, and 22 (SSH) in Security Groups.
2. **DNS Mapping**: Map your domain name or DuckDNS subdomain to the EC2 Elastic IP address.
3. **Execution**: Clone the repository and execute `chmod +x deploy.sh && ./deploy.sh`.
4. **Interactive setup**: Verify the script sets up Docker, prompts for the `.env` variables, builds images, and sets up free Let's Encrypt SSL certificates.
5. **Live Verification**:
   - Access `https://your-domain/` and log in to verify the Reflex frontend renders and communicates via WebSocket.
   - Access `https://your-domain/health` to confirm the FastAPI backend responds.
   - Perform user registration, attendance tracking, and excel uploading to verify RLS and backend connectivity.
