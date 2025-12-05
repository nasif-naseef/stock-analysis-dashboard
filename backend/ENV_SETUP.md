# Environment Configuration Guide

This guide explains how to properly configure your environment variables for the Stock Analysis Dashboard backend.

## Quick Start

1. **Copy the example file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual values (see sections below)

3. **Never commit** your `.env` file to version control (it's already in `.gitignore`)

## Required Configuration

### 1. Trading Central API Token

The most critical configuration is your Trading Central API token:

```bash
TRADING_CENTRAL_TOKEN=your_actual_token_here
```

**Get your token from:** https://api.tradingcentral.com/

⚠️ **IMPORTANT:** Never commit your actual API token to Git!

### 2. Database Configuration

Configure your PostgreSQL database connection:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

**Example for local development:**
```bash
DATABASE_URL=postgresql://stockuser:stockpass@localhost:5432/stockdb
```

**Example for Docker:**
```bash
DATABASE_URL=postgresql://stockuser:stockpass@db:5432/stockdb
```

### 3. CORS Configuration

⚠️ **CRITICAL:** Proper CORS configuration is essential for frontend communication.

#### Development Setup

For local development with React frontend:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Production Setup

For production, use your actual domain(s):

```bash
# Single domain
CORS_ORIGINS=https://yourdomain.com

# Multiple domains (include www and non-www if needed)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com
```

#### CORS Troubleshooting

**Problem:** "CORS policy: No 'Access-Control-Allow-Origin' header is present"

**Solutions:**
1. Ensure `CORS_ORIGINS` includes your frontend URL (including protocol and port)
2. Check for trailing slashes (remove them)
3. Verify no extra whitespace in the environment variable
4. For development, try: `CORS_ORIGINS=http://localhost:3000`
5. For testing, you can temporarily use `CORS_ORIGINS=*` (NOT for production!)

**Valid Examples:**
```bash
✓ CORS_ORIGINS=http://localhost:3000
✓ CORS_ORIGINS=http://localhost:3000,http://localhost:8080
✓ CORS_ORIGINS=https://yourdomain.com
✓ CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

**Invalid Examples:**
```bash
✗ CORS_ORIGINS=localhost:3000  # Missing protocol
✗ CORS_ORIGINS=http://localhost:3000/  # Trailing slash
✗ CORS_ORIGINS=  # Empty (will default to *)
```

## Optional Configuration

### Stock Tickers

Comma-separated list of stock tickers to track:

```bash
TICKERS=AAPL,TSLA,NVDA,GOOGL,MSFT
```

### Data Collection

Control how often data is collected:

```bash
COLLECTION_INTERVAL_HOURS=1  # Collect every 1 hour
MAX_RETRIES=3                 # Retry failed requests 3 times
RETRY_DELAY_SECONDS=60        # Wait 60 seconds between retries
RUN_INITIAL_COLLECTION=true   # Run collection on startup
```

### API Rate Limiting

Configure API performance settings:

```bash
API_RATE_LIMIT=100      # Max 100 requests per second
API_TIMEOUT=10          # 10 second timeout
CACHE_TTL_SECONDS=300   # Cache for 5 minutes
HISTORICAL_DAYS=1825    # Fetch 5 years of history
```

### Feature Flags

Enable or disable optional features:

```bash
ENABLE_EMAIL_ALERTS=false
ENABLE_SLACK_NOTIFICATIONS=false
DEBUG=true  # Set to false in production
```

## Complete Example

### Development `.env` File

```bash
# Database
DATABASE_URL=postgresql://stockuser:stockpass@localhost:5432/stockdb

# API Token (REPLACE WITH YOUR TOKEN!)
TRADING_CENTRAL_TOKEN=your_trading_central_token_here

# Tickers
TICKERS=AAPL,TSLA,NVDA

# Collection
COLLECTION_INTERVAL_HOURS=1
MAX_RETRIES=3
RETRY_DELAY_SECONDS=60
RUN_INITIAL_COLLECTION=true

# API Settings
API_RATE_LIMIT=100
API_TIMEOUT=10
CACHE_TTL_SECONDS=300
HISTORICAL_DAYS=1825

# CORS (Local Development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Features
ENABLE_EMAIL_ALERTS=false
ENABLE_SLACK_NOTIFICATIONS=false
DEBUG=true

# App Info
APP_NAME=Stock Analysis API
APP_VERSION=1.0.0
```

### Production `.env` File

```bash
# Database (use environment-specific values)
DATABASE_URL=postgresql://stockuser_prod:secure_password@db:5432/stockdb_prod

# API Token (use your production token)
TRADING_CENTRAL_TOKEN=your_production_token_here

# Tickers
TICKERS=AAPL,TSLA,NVDA,GOOGL,MSFT

# Collection
COLLECTION_INTERVAL_HOURS=1
MAX_RETRIES=3
RETRY_DELAY_SECONDS=60
RUN_INITIAL_COLLECTION=true

# API Settings
API_RATE_LIMIT=100
API_TIMEOUT=10
CACHE_TTL_SECONDS=300
HISTORICAL_DAYS=1825

# CORS (Production Domain)
CORS_ORIGINS=https://yourdomain.com

# Features
ENABLE_EMAIL_ALERTS=false
ENABLE_SLACK_NOTIFICATIONS=false
DEBUG=false  # Disable debug in production

# App Info
APP_NAME=Stock Analysis API
APP_VERSION=1.0.0
```

## Testing Your Configuration

After setting up your `.env` file, test the configuration:

```bash
# Start the backend server
cd backend
uvicorn app.main:app --reload

# Check if server started successfully
curl http://localhost:8000/health

# Test CORS (replace with your frontend URL)
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/v1/collection/tickers
```

## Security Best Practices

1. ✅ Never commit `.env` files with real credentials
2. ✅ Use different tokens for development and production
3. ✅ Rotate API tokens regularly
4. ✅ Use strong database passwords
5. ✅ In production, use specific CORS origins (never `*`)
6. ✅ Set `DEBUG=false` in production
7. ✅ Use environment-specific configuration files
8. ✅ Store production secrets in secure vaults (e.g., AWS Secrets Manager, Azure Key Vault)

## Troubleshooting

### CORS Issues

**Symptom:** Frontend can't connect to backend API

**Check:**
1. Verify `CORS_ORIGINS` includes your frontend URL
2. Check browser console for CORS errors
3. Test with curl (see Testing section above)
4. Temporarily set `CORS_ORIGINS=*` to isolate the issue

### Database Connection Issues

**Symptom:** "Database initialization failed"

**Check:**
1. Verify PostgreSQL is running
2. Check `DATABASE_URL` format
3. Verify credentials are correct
4. Check database exists: `psql -U stockuser -d stockdb`

### API Token Issues

**Symptom:** "No Trading Central ID configured" errors

**Check:**
1. Verify `TRADING_CENTRAL_TOKEN` is set
2. Check token is valid (not expired)
3. Test token directly with Trading Central API

## Need Help?

- Check the main README.md for general setup instructions
- Review logs: `tail -f logs/app.log`
- Enable debug mode: `DEBUG=true`
- Check API docs: http://localhost:8000/docs
