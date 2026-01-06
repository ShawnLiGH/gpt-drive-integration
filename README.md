# GPT-Drive Integration Service

Automatically saves AI Learning Coordinator GPT outputs directly to Google Drive.

## Overview

This service acts as a bridge between your Custom GPT and Google Drive, enabling automatic saving of learning session outputs without manual copy-paste.

## Features

- ✓ Automatic saving of GPT outputs to Google Drive
- ✓ Organized folder structure
- ✓ Markdown file support
- ✓ OAuth 2.0 authentication
- ✓ RESTful API with authentication
- ✓ Web-based authorization flow
- ✓ Health check endpoint

## Quick Start

### 1. Deploy to Railway (Recommended)

1. Fork this repository to your GitHub account
2. Sign up at [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Railway will auto-detect and deploy

### 2. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```
FLASK_SECRET_KEY=<generate-random-key>
API_KEY=<generate-random-key>
DRIVE_FOLDER_NAME=AI Learning Coordinator Outputs
REDIRECT_URI=https://your-app.railway.app/oauth2callback
GOOGLE_CREDENTIALS_JSON=<paste-entire-json-from-google-cloud>
```

### 3. Generate Secret Keys

Run these commands in any Python environment or use online Python: https://www.online-python.com/

```python
import secrets
print("FLASK_SECRET_KEY:", secrets.token_hex(32))
print("API_KEY:", secrets.token_urlsafe(32))
```

### 4. Setup Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "gpt-drive-integration"
3. Enable "Google Drive API"
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `https://your-app.railway.app/oauth2callback`
5. Download credentials JSON
6. Copy entire JSON content to `GOOGLE_CREDENTIALS_JSON` variable (as single line)

### 5. Authorize Google Drive

1. Visit: `https://your-app.railway.app`
2. Click "Authorize with Google Drive"
3. Complete Google OAuth flow
4. Copy the token JSON displayed
5. Add to Railway as `GOOGLE_TOKEN_JSON` variable

### 6. Configure Your GPT

See `GPT_SETUP.md` for complete instructions on:
- OpenAPI schema configuration
- Authentication setup
- Custom instructions update

## API Endpoints

### POST /save-content

Save content to Google Drive.

**Headers:**
```
Content-Type: application/json
X-API-Key: <your-api-key>
```

**Request Body:**
```json
{
  "content": "Your content here",
  "filename": "Day_01_Week_1_Foundations.md",
  "file_type": "text/markdown"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "1ABC...",
  "link": "https://drive.google.com/file/d/1ABC.../view",
  "filename": "Day_01_Week_1_Foundations.md",
  "folder": "AI Learning Coordinator Outputs",
  "message": "Successfully saved to Google Drive"
}
```

### GET /health

Check service status.

**Response:**
```json
{
  "status": "running",
  "authorized": true,
  "drive_folder": "AI Learning Coordinator Outputs",
  "api_key_configured": true
}
```

### GET /authorize

Start Google OAuth flow.

### GET /oauth2callback

OAuth callback endpoint (automatically called by Google).

## Deployment Options

### Option 1: Railway (Recommended)

- $5/month free credit
- Automatic HTTPS
- Easy environment variables
- Instant deployments

**Deploy Button:**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR-USERNAME/gpt-drive-integration)

### Option 2: Render.com

- Free tier available
- Automatic deployments
- Built-in SSL

**Steps:**
1. Sign up at [Render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Configure environment variables
5. Deploy

### Option 3: Local Development

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/gpt-drive-integration.git
cd gpt-drive-integration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cp .env.example .env
# Edit .env with your values

# Run application
python main.py
```

Visit: http://localhost:8080

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Yes | Flask session secret | Random hex string |
| `API_KEY` | Yes | GPT authentication key | Random URL-safe string |
| `DRIVE_FOLDER_NAME` | No | Target folder name | "AI Learning Coordinator Outputs" |
| `REDIRECT_URI` | Yes | OAuth callback URL | "https://app.railway.app/oauth2callback" |
| `GOOGLE_CREDENTIALS_JSON` | Yes | OAuth credentials | JSON from Google Cloud |
| `GOOGLE_TOKEN_JSON` | After auth | Refresh token | Generated after OAuth |

## Troubleshooting

### Issue: "Not Authorized" Error

**Solution:**
1. Visit: `https://your-url/authorize`
2. Complete OAuth flow
3. Copy token JSON
4. Add to `GOOGLE_TOKEN_JSON` environment variable

### Issue: "401 Unauthorized - Invalid API Key"

**Solution:**
- Verify API_KEY in deployment matches GPT configuration
- Check for extra spaces
- Regenerate if needed

### Issue: "Missing GOOGLE_CREDENTIALS_JSON"

**Solution:**
- Verify environment variable is set
- Check JSON is valid (use jsonlint.com)
- Ensure single line (no line breaks)

### Issue: OAuth Redirect Mismatch

**Solution:**
- In Google Cloud, verify redirect URI exactly matches deployment URL
- Must be HTTPS (not HTTP)
- No trailing slashes

### Issue: Cold Starts (Render Free Tier)

**Solution:**
- Render free tier sleeps after inactivity
- First request after idle takes 50+ seconds
- Upgrade to paid tier or use Railway

## Security Best Practices

1. **Never commit credentials to Git**
2. **Rotate keys periodically**
3. **Use environment variables only**
4. **Keep API_KEY secret**
5. **GOOGLE_TOKEN_JSON is sensitive** - treat as password
6. **Enable 2FA on Google account**
7. **Review Google account permissions regularly**

## File Structure

```
gpt-drive-integration/
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
├── railway.json           # Railway configuration
├── render.yaml            # Render configuration
├── Procfile               # Process configuration
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── GPT_SETUP.md          # GPT configuration guide
└── DEPLOYMENT_GUIDE.md   # Detailed deployment instructions
```

## Cost Estimate

- **Railway**: $5/month free credit (sufficient)
- **Render**: Free tier with cold starts
- **Google Drive API**: Free (standard usage)
- **Total**: $0-5/month

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/gpt-drive-integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR-USERNAME/gpt-drive-integration/discussions)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## Changelog

### v1.0.0 (2026-01-06)
- Initial release
- Google Drive integration
- OAuth 2.0 authentication
- Custom GPT support
- Railway/Render deployment

## Acknowledgments

- Built for AI Learning Coordinator GPT
- Uses Google Drive API v3
- Flask web framework
- Railway/Render hosting platforms
