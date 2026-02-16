#!/bin/bash
# Generate secure secrets for WebTics production deployment

echo "🔐 Generating secure secrets for WebTics..."
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  Warning: .env file already exists!"
    read -p "Overwrite existing .env file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled. Existing .env file not modified."
        exit 1
    fi
fi

# Generate secrets using Python
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
WITHDRAWAL_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

# Create .env file
cat > .env <<EOF
# WebTics Production Secrets
# Generated: $(date)
# NEVER commit this file to git!

ENVIRONMENT=production

# Database
POSTGRES_USER=webtics
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=webtics
DATABASE_URL=postgresql://webtics:${POSTGRES_PASSWORD}@db:5432/webtics

# API Security
WEBTICS_API_KEY=${API_KEY}
SECRET_KEY=${SECRET_KEY}

# Research Ethics
WITHDRAWAL_SECRET_KEY=${WITHDRAWAL_SECRET}

# CORS (update with your actual domain)
ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ Secrets generated and saved to .env"
echo ""
echo "📋 Your API Key (save this for clients):"
echo "   ${API_KEY}"
echo ""
echo "⚠️  IMPORTANT SECURITY NOTES:"
echo "   1. Keep .env file secure (never commit to git)"
echo "   2. Share API key securely with authorized clients only"
echo "   3. Update ALLOWED_ORIGINS in .env with your actual domain"
echo "   4. In production, consider using a secrets manager (e.g., AWS Secrets Manager)"
echo ""
echo "🔒 File permissions set to 600 (owner read/write only)"
chmod 600 .env

echo ""
echo "✨ Ready for production deployment!"
