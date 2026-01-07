# Custom GPT Configuration Guide

This guide walks you through configuring your Custom GPT to automatically save learning outputs to Google Drive.

## Prerequisites

- Deployed backend service (Railway or Render)
- Backend service authorized with Google Drive
- API_KEY from environment variables

## Step 1: OpenAPI Schema

1. Open your Custom GPT in ChatGPT
2. Click "Configure"
3. Navigate to "Actions" section
4. Click "Create new action"
5. Paste the following OpenAPI schema:

```yaml
openapi: 3.1.0
info:
  title: Google Drive Content Saver
  description: Saves learning coordinator outputs to Google Drive
  version: 1.0.0
servers:
  - url: https://web-production-499a6.up.railway.app
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
                  description: MIME type of the file
                  default: text/markdown
                folder_name:
                  type: string
                  description: Google Drive folder name
                  default: "AI Learning Coordinator Outputs"
      responses:
        "200":
          description: File saved successfully
        "401":
          description: Unauthorized
```

**Important:** Replace `REPLACE_WITH_YOUR_RAILWAY_OR_RENDER_URL` with your actual deployment URL (e.g., `https://gpt-drive-integration-production.up.railway.app`)

## Step 2: Authentication Setup

1. In the same Actions page, scroll to "Authentication" section
2. Select "API Key"
3. Configure as follows:
   - **Auth Type**: Custom
   - **Custom Header Name**: `X-API-Key`
   - **API Key**: [Paste your API_KEY from Railway/Render environment variables]
4. Click "Save"

### Where to Find Your API_KEY

**Railway:**
1. Go to your project dashboard
2. Click "Variables" tab
3. Find and copy the value of `API_KEY`

**Render:**
1. Go to your web service dashboard
2. Click "Environment" tab
3. Find and copy the value of `API_KEY`

## Step 3: Update GPT Instructions

Add the following to the **END** of your GPT's custom instructions:

```
## Output Saving Protocol

At the end of each daily learning session, automatically save the complete output using the saveToDrive action with these exact parameters:

**Required parameters:**
- filename: "Day_[XX]_Week_[Y]_[Topic].md" 
  - Format: Zero-padded day number, week number, descriptive topic
  - Examples: "Day_01_Week_1_Foundations.md", "Day_15_Week_3_Equipment_Branching.md"
- content: The complete daily output including all sections (Day/Week, Concept, Task, Practice, Review Checklist, Forward Link)
- file_type: "text/markdown"

**After saving:**
1. Confirm successful save to user
2. Provide the Google Drive link
3. State: "✓ Output automatically saved to Google Drive: [link]"

**Error handling:**
- If save fails, inform user of the error
- Continue session normally
- Suggest user check backend service authorization status

**Do not ask permission** - automatically save after generating the daily output.
```

## Step 4: Test the Integration

1. Start a new conversation with your GPT
2. Use this test prompt:

```
Create a test session output with Day 1 content about AI Fundamentals and save it with filename "Test_Integration.md"
```

3. The GPT should:
   - Generate test content
   - Automatically call the saveToDrive action
   - Return a Google Drive link
   - Confirm successful save

4. Click the link to verify the file appears in your Google Drive

## Step 5: Verify Saved Files

1. Open Google Drive: https://drive.google.com
2. Look for folder: "AI Learning Coordinator Outputs"
3. Verify test file appears
4. Check file content is correct

## Advanced Configuration (Optional)

### Change File Format

To save as Google Docs instead of Markdown:

```yaml
file_type: "application/vnd.google-apps.document"
```

### Custom Folder Name

In your backend environment variables, change:

```
DRIVE_FOLDER_NAME=Your Custom Folder Name
```

### Automatic Subfolders by Week

Modify the filename pattern in GPT instructions:

```
filename: "Week_[Y]/Day_[XX]_[Topic].md"
```

Note: This requires backend code modification to handle folder creation.

## Filename Conventions

**Standard format:**
```
Day_[XX]_Week_[Y]_[Topic].md
```

**Examples:**
```
Day_01_Week_1_Foundations.md
Day_02_Week_1_LLM_Basics.md
Day_05_Week_1_Prompt_Engineering.md
Day_08_Week_2_Structured_Outputs.md
Day_15_Week_3_Equipment_Branching.md
```

**Benefits:**
- Alphabetically sorted
- Easy to find by day or week
- Descriptive topic names
- Consistent file extension

## Troubleshooting

### GPT Can't Call the Action

**Check:**
1. OpenAPI schema URL is correct
2. API Key is properly configured
3. Backend service is running (visit health endpoint)

**Test backend manually:**
```bash
curl -X POST https://your-url.railway.app/save-content \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "content": "Test content",
    "filename": "test.md",
    "file_type": "text/markdown"
  }'
```

### Action Returns 401 Error

**Solution:**
1. Verify API_KEY matches between:
   - Railway/Render environment variables
   - GPT Authentication configuration
2. Check for extra spaces or line breaks
3. Regenerate API key if needed

### Action Returns "Not Authorized"

**Solution:**
1. Visit: `https://your-url/authorize`
2. Complete OAuth flow
3. Copy token JSON
4. Add to `GOOGLE_TOKEN_JSON` in environment variables
5. Redeploy service

### Files Not Appearing in Drive

**Check:**
1. Backend service is authorized (visit /health endpoint)
2. Folder name matches environment variable
3. Google account used for OAuth has Drive access
4. Check Google Drive trash folder

### GPT Doesn't Auto-Save

**Solution:**
1. Verify instructions were added correctly
2. Check if GPT is waiting for permission (update instructions to skip asking)
3. Test with explicit command: "Save this output to Drive"

## Security Considerations

1. **API Key Protection**
   - Never share your API_KEY
   - Rotate periodically
   - Keep in environment variables only

2. **OAuth Token**
   - GOOGLE_TOKEN_JSON is sensitive
   - Treat as password
   - Don't share or commit to Git

3. **Access Control**
   - Only you can access your GPT's saved files
   - Files saved to your personal Google Drive
   - Review Google account permissions regularly

## Integration Testing Checklist

- [ ] Backend service deployed and running
- [ ] Google Drive authorized (green status on homepage)
- [ ] API_KEY configured in GPT Actions
- [ ] OpenAPI schema URL updated with deployment URL
- [ ] Test save successful
- [ ] File appears in Google Drive
- [ ] File content is correct
- [ ] Automatic save works without prompting
- [ ] Error handling works (test with invalid filename)

## Daily Usage Workflow

**Expected flow for each learning session:**

1. User completes daily learning session with GPT
2. GPT generates complete daily output
3. GPT automatically calls saveToDrive action
4. Backend saves to Google Drive
5. GPT confirms with Drive link
6. User can click link to view in Drive

**No manual steps required after initial setup!**

## Support

If you encounter issues:

1. Check backend service logs (Railway/Render dashboard)
2. Test health endpoint: `https://your-url/health`
3. Verify environment variables are set correctly
4. Review Google Cloud Console for API errors
5. Check ChatGPT action logs in GPT configuration

## Updates and Maintenance

**Backend updates:**
1. Pull latest changes from GitHub
2. Railway/Render auto-deploys
3. No configuration changes needed

**GPT updates:**
1. Actions persist across GPT edits
2. Re-authorize if switching deployment URLs
3. Update instructions as needed for workflow changes

## Example: Complete Working Setup

**Backend Environment Variables:**
```
FLASK_SECRET_KEY=abc123...
API_KEY=xyz789...
DRIVE_FOLDER_NAME=AI Learning Coordinator Outputs
REDIRECT_URI=https://my-app.railway.app/oauth2callback
GOOGLE_CREDENTIALS_JSON={"web":{...}}
GOOGLE_TOKEN_JSON={"token":"...","refresh_token":"..."}
```

**GPT Action URL:**
```
https://my-app.railway.app
```

**GPT API Key:**
```
xyz789...  (matches API_KEY above)
```

**Test Command:**
```
"Generate Day 1 foundations content and save it"
```

**Expected Response:**
```
[Generated content]

✓ Output automatically saved to Google Drive: https://drive.google.com/file/d/1ABC.../view
```

---

**You're all set!** Your GPT will now automatically save all learning outputs to Google Drive.
