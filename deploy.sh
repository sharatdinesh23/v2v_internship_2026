#!/bin/bash

# 🚀 Automated Production Deployment Script: Internship Portal
# Optimized for AWS Free Tier (EC2 t2.micro/t3.micro Ubuntu instances)

set -e

# --- Color Definitions & Icons ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

INFO="[${CYAN}INFO${NC}]"
SUCCESS="[${GREEN}SUCCESS${NC}]"
WARNING="[${YELLOW}WARNING${NC}]"
ERROR="[${RED}ERROR${NC}]"

echo -e "${CYAN}========================================================================${NC}"
echo -e "${CYAN}🚀  Internship Portal AWS Free Tier Auto-Deployment Tool  🚀${NC}"
echo -e "${CYAN}========================================================================${NC}"

# --- 1. Root & OS Check ---
if [ "$EUID" -ne 0 ]; then
  echo -e "${ERROR} Please run this script with sudo privileges:"
  echo -e "      sudo ./deploy.sh"
  exit 1
fi

# --- 2. Automated Prerequisites Installer ---
install_docker() {
  echo -e "${INFO} Checking Docker installation..."
  if ! command -v docker &> /dev/null; then
    echo -e "${WARNING} Docker is not installed. Installing Docker..."
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    echo -e "${SUCCESS} Docker and Docker Compose installed successfully."
  else
    echo -e "${SUCCESS} Docker is already installed."
  fi
}

install_docker

# --- 3. Gather Domain & Supabase Configurations ---
echo -e "\n${CYAN}📋 Step 1: Configure Production Environment Variables${NC}"
echo -e "${CYAN}------------------------------------------------------------------------${NC}"

# Domain setup
read -p "🔹 Enter your domain name (e.g., portal.v2vclasses.com or myapp.duckdns.org): " DOMAIN_NAME
while [ -z "$DOMAIN_NAME" ]; do
  echo -e "${ERROR} Domain name cannot be empty."
  read -p "🔹 Enter your domain name: " DOMAIN_NAME
done

# Supabase setup
read -p "🔹 Enter your Supabase Project URL: " SUPABASE_URL
while [ -z "$SUPABASE_URL" ]; do
  echo -e "${ERROR} Supabase URL cannot be empty."
  read -p "🔹 Enter your Supabase Project URL: " SUPABASE_URL
done

read -p "🔹 Enter your Supabase Anon Key (or Service Role Key): " SUPABASE_KEY
while [ -z "$SUPABASE_KEY" ]; do
  echo -e "${ERROR} Key cannot be empty."
  read -p "🔹 Enter your Supabase key: " SUPABASE_KEY
done

read -p "🔹 Enter your Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
while [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; do
  echo -e "${ERROR} Service Role Key cannot be empty."
  read -p "🔹 Enter your Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
done

# JWT secret setup
read -p "🔹 Enter a JWT Secret (leave blank to generate a secure random key): " JWT_SECRET
if [ -z "$JWT_SECRET" ]; then
  JWT_SECRET=$(openssl rand -hex 32)
  echo -e "${INFO} Generated secure JWT Secret: ${YELLOW}$JWT_SECRET${NC}"
fi

# Email address for Let's Encrypt updates
read -p "🔹 Enter your email address for Let's Encrypt SSL notifications: " SSL_EMAIL
while [ -z "$SSL_EMAIL" ]; do
  echo -e "${ERROR} Email address cannot be empty."
  read -p "🔹 Enter your email address: " SSL_EMAIL
done

# --- 4. Write Configuration Files ---
echo -e "\n${INFO} Writing configurations to .env files..."

# Root .env (required by docker-compose to pass build args)
cat <<EOF > .env
DOMAIN_NAME=$DOMAIN_NAME
EOF

# Backend .env
mkdir -p Backend
cat <<EOF > Backend/.env
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
JWT_SECRET=$JWT_SECRET
ALLOWED_ORIGIN=https://$DOMAIN_NAME
EOF

echo -e "${SUCCESS} Configurations written successfully."

# --- 5. Implement Dummy Certificate Bootstrapping ---
echo -e "\n${CYAN}🛡️ Step 2: Bootstrap SSL Certificates (Let's Encrypt)${NC}"
echo -e "${CYAN}------------------------------------------------------------------------${NC}"

# Path where certs reside (mapped from Docker volumes)
CERT_DIR="/var/lib/docker/volumes/$(basename $(pwd))_letsencrypt/_data/live/production"

echo -e "${INFO} Creating certificate storage directories..."
mkdir -p "/var/lib/docker/volumes/$(basename $(pwd))_letsencrypt/_data/live/production"

if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
  echo -e "${INFO} No certificates found. Generating temporary dummy certificates to bootstrap Nginx..."
  
  # Create a self-signed key/cert pair
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "$CERT_DIR/privkey.pem" \
    -out "$CERT_DIR/fullchain.pem" \
    -subj "/CN=localhost" &>/dev/null
    
  echo -e "${SUCCESS} Dummy certificates successfully created."
else
  echo -e "${INFO} Certificates already exist. Skipping dummy certificate creation."
fi

# --- 6. Launch Initial Stack ---
echo -e "\n${CYAN}📦 Step 3: Compile and Launch the Docker Stack (Port 80/443)${NC}"
echo -e "${CYAN}------------------------------------------------------------------------${NC}"
echo -e "${INFO} Building Docker containers. This will take a few minutes (installing Python + Node.js)..."

docker compose down --remove-orphans || true
docker compose build --build-arg REFLEX_API_URL=https://$DOMAIN_NAME
docker compose up -d

echo -e "${SUCCESS} Containers built and launched in background successfully."

# --- 7. Request Authentic SSL Certificates ---
echo -e "\n${CYAN}🔑 Step 4: Requesting Official Let's Encrypt SSL Certificates${NC}"
echo -e "${CYAN}------------------------------------------------------------------------${NC}"
echo -e "${INFO} Requesting real certificate for ${YELLOW}$DOMAIN_NAME${NC}..."

# Remove dummy certificates so certbot can overwrite
rm -rf "$CERT_DIR"
mkdir -p "/var/lib/docker/volumes/$(basename $(pwd))_letsencrypt/_data"

# Run Certbot container to fetch the certificate via port 80 webroot challenge
docker compose run --rm --entrypoint \
  "certbot certonly --webroot -w /var/www/certbot \
    --email $SSL_EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN_NAME" certbot

# Move official certificates to our expected Nginx location
echo -e "${INFO} Aligning certificates for Nginx production profile..."
# The certificates will be located in letsencrypt volume inside /etc/letsencrypt/live/$DOMAIN_NAME/
# We will create a symlink or folder named "production" inside letsencrypt volume to point to $DOMAIN_NAME
LE_VOLUME_DIR="/var/lib/docker/volumes/$(basename $(pwd))_letsencrypt/_data"
ln -sfn "$DOMAIN_NAME" "$LE_VOLUME_DIR/live/production"

# --- 8. Reload Nginx ---
echo -e "${INFO} Reloading Nginx with authentic production SSL certificates..."
docker compose exec nginx nginx -s reload

echo -e "\n${GREEN}========================================================================${NC}"
echo -e "${GREEN}🎉 CONGRATULATIONS! DEPLOYMENT COMPLETED SUCCESSFULLY 🎉${NC}"
echo -e "${GREEN}========================================================================${NC}"
echo -e "🌐 Your website is now live at:       ${CYAN}https://$DOMAIN_NAME/${NC}"
echo -e "🟢 FastAPI Backend Health Check at:  ${CYAN}https://$DOMAIN_NAME/health${NC}"
echo -e "🔒 SSL is active and auto-renewing every 12 hours."
echo -e "📂 Supabase Database remains configured in high-performance cloud storage."
echo -e "${GREEN}========================================================================${NC}\n"
EOF
