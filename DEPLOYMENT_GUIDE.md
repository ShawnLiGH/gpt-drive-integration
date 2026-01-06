# Complete Deployment Guide

This guide provides step-by-step instructions for deploying the GPT-Drive Integration Service from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Generate Secret Keys](#step-1-generate-secret-keys)
3. [Step 2: Google Cloud Setup](#step-2-google-cloud-setup)
4. [Step 3: GitHub Repository Setup](#step-3-github-repository-setup)
5. [Step 4: Deploy to Railway](#step-4-deploy-to-railway)
6. [Step 5: Configure Environment Variables](#step-5-configure-environment-variables)
7. [Step 6: Update Google OAuth](#step-6-update-google-oauth)
8. [Step 7: Authorize Google Drive](#step-7-authorize-google-drive)
9. [Step 8: Configure Custom GPT](#step-8-configure-custom-gpt)
10. [Step 9: Test Everything](#step-9-test-everything)
11. [Alternative: Render Deployment](#alternative-render-deployment)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required:**
- GitHub account
- Google account
- ChatGPT Plus subscription (for Custom GPT)

**No local development environment needed!**

---

## Step 1: Generate Secret Keys

### 1.1 Use Online Python

Go to: https://www.online-python.com/

### 1.2 Run This Code

```python
import secrets

print("=" * 70)
print("COPY THESE VALUES - YOU'LL NEED THEM LATER")
print("=" * 70)
print()
print("FLASK_SECRET_KEY:")
print(secrets.token_hex(32))
print()
print("API_KEY:")
print(secrets.token_urlsafe(32))
print()
print("=" * 70)
```

### 1.3 Save the Output

Copy both keys to a text file. You'll need them in Step 5.

**Example output:**
```
FLASK_SECRET_KEY:
a1b2c3d4e5f6...

API_KEY:
XyZ123AbC456...
```

---

## Step 2: Google Cloud Setup

### 2.1 Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click "Select a project" (top bar)
3. Click "NEW PROJECT"
4. Project name: `gpt-drive-integration`
5. Click "CREATE"
6. Wait for project creation (takes 30 seconds)

### 2.2 Enable Google Drive API

1. Make sure your new project is selected (top bar)
2. Go to: "APIs & Services" → "Library"
3. Search: `Google Drive API`
4. Click on "Google Drive API"
5. Click "ENABLE"
6. Wait for enablement (takes 10 seconds)

### 2.3 Configure OAuth Consent Screen

1. Go to: "APIs & Services" → "OAuth consent screen"
2. User Type: Select "External"
3. Click "CREATE"

**App information:**
- App name: `GPT Drive Integration`
- User support email: [Your email]
- Developer contact information: [Your email]

4. Click "SAVE AND CONTINUE"
5. Scopes: Click "SAVE AND CONTINUE" (skip this step)
6. Test users: Click "SAVE AND CONTINUE" (skip this step)
7. Summary: Click "BACK TO DASHBOARD"

### 2.4 Create OAuth Credentials (Temporary)

1. Go to: "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Application type: "Web application"
4. Name: `GPT Drive Client`
5. Authorized redirect URIs: 
   - Click "ADD URI"
   - Enter: `https://PLACEHOLDER.railway.app/oauth2callback`
   - (You'll update this later with your real URL)
6. Click "CREATE"

### 2.5 Download Credentials

1. A popup appears with Client ID and Client Secret
2. Click "DOWNLOAD JSON"
3. Save the file as `credentials.json`
4. **Keep this file safe** - you'll need it in Step 5

---

## Step 3: GitHub Repository Setup

### 3.1 Create New Repository

1. Go to: https://github.com/new
2. Repository name: `gpt-drive-integration`
3. Description: `Bridge between Custom GPT and Google Drive`
4. Public or Private: **Your choice**
5. Do **NOT** check "Add a README file"
6. Do **NOT** check "Add .gitignore"
7. Click "Create repository"

### 3.2 Upload Files

**Method A: Web Upload (Easiest)**

1. On your new repository page, click "uploading an existing file"
2. Drag and drop all files from the downloaded package:
   - `main.py`
   - `requirements.txt`
   - `railway.json`
   - `render.yaml`
   - `Procfile`
   - `.env.example`
   - `.gitignore`
   - `README.md`
   - `GPT_SETUP.md`
   - `DEPLOYMENT_GUIDE.md`
3. Commit message: "Initial commit"
4. Click "Commit changes"

**Method B: Git Command Line** (If you prefer)

```bash
git clone https://github.com/YOUR-USERNAME/gpt-drive-integration.git
cd gpt-drive-integration
# Copy all files into this directory
git add .
git commit -m "Initial commit"
git push origin main
```

---

## Step 4: Deploy to Railway

### 4.1 Sign Up for Railway

1. Go to: https://railway.app/
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your GitHub account

### 4.2 Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Click "Configure GitHub App"
4. Select "Only select repositories"
5. Choose `gpt-drive-integration`
6. Click "Install & Authorize"

### 4.3 Deploy Repository

1. Back in Railway, select `gpt-drive-integration` repository
2. Railway will automatically:
   - Detect Python
   - Install dependencies
   - Start deployment
3. Wait for deployment (takes 2-3 minutes)
4. Status will show "Active" when complete

### 4.4 Generate Domain

1. Click on your service in Railway dashboard
2. Go to "Settings" tab
3. Scroll down to "Networking" → "Domains"
4. Click "Generate Domain"
5. Copy the generated URL (e.g., `https://gpt-drive-integration-production.up.railway.app`)
6. **Save this URL** - you'll need it multiple times

---

## Step 5: Configure Environment Variables

### 5.1 Navigate to Variables

1. In Railway dashboard, click on your service
2. Click "Variables" tab
3. Click "New Variable"

### 5.2 Add Each Variable

Add these variables one by one:

**Variable 1: FLASK_SECRET_KEY**
```
Name: FLASK_SECRET_KEY
Value: [Paste from Step 1]
```

**Variable 2: API_KEY**
```
Name: API_KEY
Value: [Paste from Step 1]
```

**Variable 3: DRIVE_FOLDER_NAME**
```
Name: DRIVE_FOLDER_NAME
Value: AI Learning Coordinator Outputs
```

**Variable 4: REDIRECT_URI**
```
Name: REDIRECT_URI
Value: https://YOUR-RAILWAY-URL.railway.app/oauth2callback
```
Replace `YOUR-RAILWAY-URL` with your actual Railway URL from Step 4.4.

**Variable 5: GOOGLE_CREDENTIALS_JSON**

This one is tricky. You need to format the credentials.json file as a single line.

1. Open the `credentials.json` file you downloaded in Step 2.5
2. Copy the ENTIRE contents
3. Remove all line breaks (make it one long line)
4. Paste as the value

**Example:**
```
Name: GOOGLE_CREDENTIALS_JSON
Value: {"web":{"client_id":"123456789...","project_id":"gpt-drive-integration","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"GOCSPX-abc123...","redirect_uris":["https://YOUR-URL.railway.app/oauth2callback"]}}
```

### 5.3 Deploy Changes

Railway will automatically redeploy after you add variables. Wait for deployment to complete.

---

## Step 6: Update Google OAuth

Now that you have your real Railway URL, update Google Cloud:

### 6.1 Go Back to Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Select project: `gpt-drive-integration`
3. Go to: "APIs & Services" → "Credentials"

### 6.2 Update OAuth Client

1. Click on your OAuth 2.0 Client ID (e.g., "GPT Drive Client")
2. Under "Authorized redirect URIs":
   - Remove: `https://PLACEHOLDER.railway.app/oauth2callback`
   - Add: `https://YOUR-ACTUAL-RAILWAY-URL.railway.app/oauth2callback`
3. Click "SAVE"

---

## Step 7: Authorize Google Drive

### 7.1 Visit Your Service

1. Open browser
2. Go to: `https://YOUR-RAILWAY-URL.railway.app`
3. You should see the service status page

### 7.2 Start Authorization

1. Click "Authorize with Google Drive" button
2. You'll be redirected to Google sign-in
3. Sign in with your Google account
4. Review permissions requested:
   - "See, edit, create, and delete only the specific Google Drive files you use with this app"
5. Click "Continue" or "Allow"

### 7.3 Copy Token

After successful authorization, you'll see a page with:
- Success message
- A JSON token in a box

**Copy the entire JSON token** (it looks like this):

```json
{
  "token": "ya29.a0AfB_...",
  "refresh_token": "1//0gXyZ...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789...",
  "client_secret": "GOCSPX-abc123...",
  "scopes": ["https://www.googleapis.com/auth/drive.file"]
}
```

### 7.4 Add Token to Railway

1. Go back to Railway dashboard
2. Click "Variables" tab
3. Click "New Variable"
4. Name: `GOOGLE_TOKEN_JSON`
5. Value: [Paste the JSON token you just copied]
6. Railway will automatically redeploy

### 7.5 Verify Authorization

1. Wait for redeployment (1-2 minutes)
2. Go back to: `https://YOUR-RAILWAY-URL.railway.app`
3. Status should now show: "✓ Authorized"
4. Drive API should show: "Connected"

---

## Step 8: Configure Custom GPT

### 8.1 Open Your GPT

1. Go to: https://chat.openai.com/
2. Navigate to your "AI Engineering Learning Coordinator" GPT
3. Click "Configure" (top right)

### 8.2 Add Action

1. Scroll to "Actions" section
2. Click "Create new action"
3. In the schema editor, paste this (replace URL):

```yaml
openapi: 3.0.0
info:
  title: Google Drive Content Saver
  description: Saves learning coordinator outputs to Google Drive
  version: 1.0.0
servers:
  - url: https://YOUR-RAILWAY-URL.railway.app
    description: Production server

paths:
  /save-content:
    post:
      operationId: saveToDrive
      summary: Save content to Google Drive
      description: Saves the daily learning output to Google Drive folder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - content
                - filename
              properties:
                content:
                  type: string
                  description: The complete text content to save
                filename:
                  type: string
                  description: Filename with extension
                file_type:
                  type: string
                  description: MIME type
                  default: "text/markdown"
                  enum:
                    - "text/plain"
                    - "text/markdown"
                    - "application/vnd.google-apps.document"
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  file_id:
                    type: string
                  link:
                    type: string
                  message:
                    type: string
        '401':
          description: Unauthorized

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - ApiKeyAuth: []
```

Replace `YOUR-RAILWAY-URL` with your actual Railway URL.

### 8.3 Configure Authentication

1. Scroll down in the same page
2. Under "Authentication", click dropdown
3. Select "API Key"
4. Auth Type: "Custom"
5. Custom Header Name: `X-API-Key`
6. API Key: [Paste your API_KEY from Step 1]
7. Click "Save"

### 8.4 Update Instructions

1. Click "Configure" (if not already there)
2. Scroll to "Instructions" section
3. **Add to the END** of existing instructions:

```
## Output Saving Protocol

At the end of each daily learning session, automatically save the complete output using the saveToDrive action:

- filename: "Day_[XX]_Week_[Y]_[Topic].md"
- content: Complete daily output with all sections
- file_type: "text/markdown"

After saving, confirm with: "✓ Output saved to Google Drive: [link]"
```

4. Click "Save" (top right)

---

## Step 9: Test Everything

### 9.1 Test Backend Health

Visit: `https://YOUR-RAILWAY-URL.railway.app/health`

Should return:
```json
{
  "status": "running",
  "authorized": true,
  "drive_folder": "AI Learning Coordinator Outputs",
  "api_key_configured": true
}
```

### 9.2 Test GPT Integration

1. Start a new chat with your GPT
2. Send this message:

```
Create a test output for Day 1 about AI Fundamentals and save it with filename "Test_Integration.md"
```

3. GPT should:
   - Generate content
   - Call saveToDrive action
   - Return a Google Drive link
   - Show confirmation

### 9.3 Verify in Google Drive

1. Open: https://drive.google.com
2. Look for folder: "AI Learning Coordinator Outputs"
3. Find file: "Test_Integration.md"
4. Open and verify content

**✓ If all checks pass, you're done!**

---

## Alternative: Render Deployment

If you prefer Render.com over Railway:

### Render Steps:

1. Go to: https://render.com/
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect repository: `gpt-drive-integration`
5. Configure:
   - Name: `gpt-drive-integration`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
6. Add all environment variables (same as Railway)
7. Click "Create Web Service"
8. Wait for deployment
9. Copy the Render URL (e.g., `https://gpt-drive-integration.onrender.com`)
10. Update Google OAuth redirect URI
11. Continue from Step 7

**Note:** Render free tier has cold starts (first request after idle takes 50+ seconds).

---

## Troubleshooting

### Problem: Can't access Railway URL

**Solution:**
- Wait 2-3 minutes after deployment
- Check Railway logs for errors
- Verify all environment variables are set

### Problem: OAuth returns "redirect_uri_mismatch"

**Solution:**
- Verify redirect URI in Google Cloud exactly matches Railway URL
- Must be HTTPS (not HTTP)
- No trailing slashes
- Check for typos

### Problem: "Not Authorized" after OAuth

**Solution:**
- Make sure you copied GOOGLE_TOKEN_JSON correctly
- Check for line breaks (should be single line)
- Verify JSON is valid (use jsonlint.com)
- Redeploy Railway after adding token

### Problem: GPT action returns 401

**Solution:**
- Verify API_KEY in GPT matches Railway variable
- Check for extra spaces
- API key is case-sensitive

### Problem: Files don't appear in Drive

**Solution:**
- Check /health endpoint shows authorized: true
- Verify folder name matches DRIVE_FOLDER_NAME variable
- Check Google account permissions
- Look in Drive trash folder

### Problem: Railway deployment fails

**Solution:**
- Check Railway logs for specific error
- Verify requirements.txt is correct
- Make sure main.py has no syntax errors
- Check Python version compatibility

---

## Quick Reference Card

**Save these for future use:**

| Item | Value |
|------|-------|
| Railway URL | https://YOUR-URL.railway.app |
| Health Check | https://YOUR-URL.railway.app/health |
| Authorization | https://YOUR-URL.railway.app/authorize |
| Google Project | gpt-drive-integration |
| Drive Folder | AI Learning Coordinator Outputs |

**Credentials to keep safe:**
- FLASK_SECRET_KEY
- API_KEY
- GOOGLE_CREDENTIALS_JSON
- GOOGLE_TOKEN_JSON

---

## Maintenance

### Rotate API Keys

Every 3-6 months:

1. Generate new keys (Step 1)
2. Update Railway variables
3. Update GPT authentication
4. Test integration

### Check Authorization

If files stop saving:

1. Visit /authorize endpoint
2. Reauthorize with Google
3. Copy new token
4. Update GOOGLE_TOKEN_JSON

### Monitor Usage

Check Railway dashboard for:
- Request logs
- Error rates
- Resource usage
- Deployment status

---

## Cost Summary

- **Railway**: $5/month free credit (sufficient for this app)
- **Render**: Free tier available (with cold starts)
- **Google Drive API**: Free for normal usage
- **Total**: $0-5/month

---

## Next Steps

After successful deployment:

1. Use your GPT normally for learning sessions
2. Outputs automatically save to Drive
3. Review saved files periodically
4. Organize files in Drive as needed
5. Backup important sessions

---

**Congratulations!** Your GPT-Drive integration is now live and working.

For support, visit: [GitHub Repository Issues]
