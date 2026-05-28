# 🚀 AWS Free Tier Production Deployment Guide

This guide explains how to deploy the **FastAPI Backend** and the **Reflex Frontend & Event Server** in the **AWS Free Tier** (12-Month Free EC2 `t2.micro` or `t3.micro` instance), keeping your database hosted in the **Supabase** cloud.

```mermaid
graph TD
    Client[Web Browser] -- HTTPS (443) / WSS --> Nginx[Nginx Reverse Proxy & Static Host]
    Nginx -- Serves Static Content --> Client
    Nginx -- API Requests (/api/*) --> FastAPI[FastAPI Backend (Port 8888)]
    Nginx -- Websocket / UI State (/_event/*) --> ReflexBE[Reflex Backend Event Server (Port 8010)]
    FastAPI -- Data Operations --> Supabase[(Supabase Database & Auth)]
    ReflexBE -- API calls --> FastAPI
```

---

## 🛠️ Step 1: Provision your AWS EC2 Instance (100% Free Tier)

1. **Sign in to AWS Console**: Go to [aws.amazon.com](https://aws.amazon.com/) and sign in or create a new account (which gives you 12 months of Free Tier benefits).
2. **Launch EC2 Instance**:
   - Navigate to the **EC2 Dashboard** and click **Launch instance**.
   - **Name**: `Internship-Portal-Server`
   - **OS (AMI)**: Select **Ubuntu Server 24.04 LTS** or **22.04 LTS** (ensure it has the *Free tier eligible* tag).
   - **Instance Type**: Select **`t2.micro`** (or **`t3.micro`** if you are in a region where t3 is the default free tier type). Both provide **750 hours/month** of 100% free compute for 12 months.
   - **Key Pair**: Create a new `.pem` key pair or select an existing one to access the server via SSH.
3. **Configure Security Group (Firewall)**:
   Ensure you add the following inbound rules:
   
| Protocol | Port Range | Source | Description |
| :--- | :--- | :--- | :--- |
| **SSH** (TCP) | `22` | `My IP` or `0.0.0.0/0` | Secure shell remote access |
| **HTTP** (TCP) | `80` | `0.0.0.0/0` | Let's Encrypt challenge & HTTP redirect |
| **HTTPS** (TCP) | `443` | `0.0.0.0/0` | Secure Web traffic (Main App, API, WebSockets) |

4. **Storage**: Leave the default **30 GB** (which is the maximum free tier storage size for SSDs) and click **Launch Instance**.
5. **Assign Elastic IP (Optional but highly recommended)**:
   - Go to **Elastic IPs** in the left sidebar, click **Allocate Elastic IP address**, and click **Allocate**.
   - Select your new Elastic IP, click **Actions** -> **Associate Elastic IP address**, choose your EC2 instance, and click **Associate**. This ensures your server IP does not change when rebooted!

---

## 🌐 Step 2: Link your Hostinger Domain (Required for SSL/HTTPS)

To secure your portal with Let's Encrypt, you must point your Hostinger domain (or a subdomain) to your EC2 Elastic IP address using an A Record:

### Option A: Use your Hostinger Domain
1. Log in to your **Hostinger hPanel**.
2. Navigate to **Domains** on the top menu and select your domain name.
3. Click on **DNS / Nameservers** in the left sidebar.
4. Under the **DNS Zone Editor**, create a new record:
   - **Type**: `A`
   - **Name**: `@` (if you want the main domain, e.g., `yourdomain.com`) OR `portal` (if you want a subdomain, e.g., `portal.yourdomain.com`)
   - **Points to**: `YOUR_EC2_ELASTIC_IP`
   - **TTL**: `3600` (for fast propagation)
5. Click **Add Record** (or edit the existing `@` record if one exists).

### Option B: Use free Dynamic DNS (DuckDNS)
If you'd rather keep your main domain separate or run a quick test:
1. Go to [duckdns.org](https://www.duckdns.org/) and log in.
2. Create a subdomain (e.g., `v2v-internship.duckdns.org`).
3. Enter your EC2 Elastic IP address in the IP box and click **Update IP**.

---

## 📦 Step 3: Run the Auto-Deployment Tool on EC2

All required configurations, Docker environments, WebSocket handling, Nginx profiles, and SSL automation have been bundled into a premium shell script inside your repository: `deploy.sh`.

1. **Connect to your EC2 instance** using SSH:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_ELASTIC_IP
   ```
2. **Clone your repository** onto the server:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git portal
   cd portal
   ```
3. **Execute the auto-deployment script**:
   Make the script executable and run it with `sudo`:
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```
4. **Interactive Setup**:
   The script will:
   - Automatically install **Docker** and **Docker Compose** if missing.
   - Prompt you for your **Domain Name** (e.g., `v2v-internship.duckdns.org`).
   - Prompt you for your **Supabase URL**, **Anon Key**, and **Service Role Key**.
   - Generate a cryptographically secure random **JWT Secret** (if you leave it blank).
   - Prompt you for an email for SSL renewal notifications.
   - Build lightweight, high-performance Docker containers for FastAPI and Reflex.
   - Request real Let's Encrypt certificates and reload Nginx.

---

## 🔒 Step 4: Verify Your Deployment

Once the deployment completes, check that all services are fully operational:

1. **Main Web Portal**: Open a browser and visit `https://yourdomain.com`. It should load instantly, show a secure HTTPS lock, and connect automatically.
2. **Backend API Health Check**: Visit `https://yourdomain.com/health`. You should receive a status payload:
   ```json
   {
     "status": 200,
     "message": "OK",
     "timestamp": "2026-05-28T21:10:00.000000"
   }
   ```
3. **Docker Logs**: You can monitor active processes by running:
   ```bash
   # See all running containers
   sudo docker compose ps
   
   # Live stream logs of all services
   sudo docker compose logs -f
   
   # Check logs of a specific service (e.g., backend)
   sudo docker compose logs -f backend
   ```

---

## 🛠️ Operational Commands & Troubleshooting

### Restarting the Stack
If you need to stop or restart the services:
```bash
# Stop all services
sudo docker compose down

# Start all services
sudo docker compose up -d

# Rebuild and restart after pulling code updates
git pull
sudo docker compose down
sudo docker compose up -d --build
```

### Auto-Renewal of SSL
Your Let's Encrypt certificate will automatically renew! The `certbot` container runs in the background and checks for renewals every 12 hours. If a renewal occurs, Nginx is reloaded with no downtime.

### CORS Errors
If you see console errors relating to CORS:
- Ensure the `ALLOWED_ORIGIN` in your `Backend/.env` exactly matches your website URL including protocol (e.g. `https://v2v-internship.duckdns.org`).
- Restart the backend container: `sudo docker compose restart backend`.
