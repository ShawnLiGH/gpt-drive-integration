from flask import Flask, request, jsonify, redirect, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
import os
import json
from datetime import datetime
import secrets

app = Flask(__name__)

# Configure app to work behind a proxy (Railway/Render uses HTTPS proxy)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Security configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Configuration from environment variables
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
FOLDER_NAME = os.getenv('DRIVE_FOLDER_NAME', 'AI Learning Coordinator Outputs')
API_KEY = os.getenv('API_KEY')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8080/oauth2callback')

# Load Google credentials from environment
def get_credentials_dict():
    """Load Google OAuth credentials from environment variable"""
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not set")
    return json.loads(creds_json)

def get_drive_service():
    """Initialize Google Drive service with saved credentials"""
    creds = None
    
    # Try to load from token file or environment
    token_json = os.getenv('GOOGLE_TOKEN_JSON')
    if token_json:
        creds_info = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        return None
    
    return build('drive', 'v3', credentials=creds)

def save_token(credentials):
    """Save token to both file and environment variable"""
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Save to file
    with open(TOKEN_FILE, 'w') as token:
        json.dump(token_data, token)
    
    # Print for manual environment variable update
    print("=" * 80)
    print("IMPORTANT: Copy this token to your GOOGLE_TOKEN_JSON environment variable:")
    print("=" * 80)
    print(json.dumps(token_data))
    print("=" * 80)
    
    return token_data

def get_or_create_folder(service, folder_name):
    """Get or create the target folder in Google Drive"""
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    
    # Create new folder
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder['id']

@app.route('/')
def home():
    """Home page with status"""
    service = get_drive_service()
    authorized = service is not None
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GPT-Drive Integration Service</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; }}
            .status {{ padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .authorized {{ background: #d4edda; color: #155724; }}
            .not-authorized {{ background: #f8d7da; color: #721c24; }}
            .button {{ 
                display: inline-block; 
                padding: 10px 20px; 
                background: #007bff; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 10px 5px;
            }}
            .button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h1>GPT-Drive Integration Service</h1>
        <div class="status {'authorized' if authorized else 'not-authorized'}">
            <h2>Status: {'✓ Authorized' if authorized else '✗ Not Authorized'}</h2>
            <p>Drive API: {'Connected' if authorized else 'Not Connected'}</p>
        </div>
        
        {'<a href="/authorize" class="button">Authorize with Google Drive</a>' if not authorized else '<p>Service is ready to receive requests from your GPT.</p>'}
        
        <h3>Configuration</h3>
        <ul>
            <li>Target Folder: {FOLDER_NAME}</li>
            <li>API Key: {'Configured' if API_KEY else 'Not Set'}</li>
            <li>Redirect URI: {REDIRECT_URI}</li>
        </ul>
        
        <h3>Endpoints</h3>
        <ul>
            <li><strong>POST /save-content</strong> - Save content to Drive</li>
            <li><strong>GET /authorize</strong> - Start OAuth flow</li>
            <li><strong>GET /health</strong> - Health check</li>
        </ul>
    </body>
    </html>
    """
    return html

@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback"""
    try:
        creds_dict = get_credentials_dict()
        
        flow = Flow.from_client_config(
            client_config=creds_dict,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        
        # Save credentials
        token_data = save_token(credentials)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; }}
                .success {{ background: #d4edda; padding: 20px; border-radius: 5px; color: #155724; }}
                .token-box {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border: 1px solid #dee2e6; 
                    border-radius: 5px; 
                    margin: 20px 0;
                    font-family: monospace;
                    font-size: 12px;
                    overflow-x: auto;
                }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; color: #856404; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✓ Authorization Successful!</h1>
                <p>Your Google Drive is now connected.</p>
            </div>
            
            <div class="warning">
                <h2>⚠ Important: Update Environment Variable</h2>
                <p>Copy the token below and save it to your <strong>GOOGLE_TOKEN_JSON</strong> environment variable in Railway/Render:</p>
                <div class="token-box">{json.dumps(token_data, indent=2)}</div>
                <p>Steps:</p>
                <ol>
                    <li>Go to your Railway/Render dashboard</li>
                    <li>Find the Variables/Environment section</li>
                    <li>Update or add: <strong>GOOGLE_TOKEN_JSON</strong></li>
                    <li>Paste the JSON above</li>
                    <li>Redeploy if needed</li>
                </ol>
            </div>
            
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; margin: 50px;">
            <h1>Authorization Error</h1>
            <p style="color: red;">Error: {str(e)}</p>
            <p><a href="/authorize">Try Again</a></p>
        </body>
        </html>
        """, 500

@app.route('/authorize')
def authorize():
    """Initiate OAuth flow"""
    try:
        creds_dict = get_credentials_dict()
        
        flow = Flow.from_client_config(
            client_config=creds_dict,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; margin: 50px;">
            <h1>Configuration Error</h1>
            <p style="color: red;">Error: {str(e)}</p>
            <p>Make sure GOOGLE_CREDENTIALS_JSON environment variable is set correctly.</p>
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        """, 500

@app.route('/save-content', methods=['POST'])
def save_content():
    """Save content to Google Drive"""
    try:
        # Verify API key
        request_api_key = request.headers.get('X-API-Key')
        if not API_KEY or request_api_key != API_KEY:
            return jsonify({'error': 'Unauthorized - Invalid API Key'}), 401
        
        # Get request data
        data = request.json
        content = data.get('content')
        filename = data.get('filename')
        file_type = data.get('file_type', 'text/markdown')
        
        if not content or not filename:
            return jsonify({'error': 'Missing content or filename'}), 400
        
        # Initialize Drive service
        service = get_drive_service()
        if not service:
            return jsonify({
                'error': 'Not authorized with Google Drive',
                'message': 'Please visit the /authorize endpoint to connect your Google Drive'
            }), 401
        
        # Get or create folder
        folder_id = get_or_create_folder(service, FOLDER_NAME)
        
        # Prepare file metadata
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # Create file based on type
        if file_type == 'application/vnd.google-apps.document':
            # Convert to Google Doc
            file_metadata['mimeType'] = 'application/vnd.google-apps.document'
            media = MediaInMemoryUpload(
                content.encode('utf-8'),
                mimetype='text/plain',
                resumable=True
            )
        else:
            # Save as markdown or plain text
            media = MediaInMemoryUpload(
                content.encode('utf-8'),
                mimetype=file_type,
                resumable=True
            )
        
        # Upload file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, name'
        ).execute()
        
        return jsonify({
            'success': True,
            'file_id': file.get('id'),
            'link': file.get('webViewLink'),
            'filename': file.get('name'),
            'folder': FOLDER_NAME,
            'message': f'Successfully saved to Google Drive'
        })
    
    except Exception as e:
        app.logger.error(f"Error saving to Drive: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    service = get_drive_service()
    authorized = service is not None
    
    return jsonify({
        'status': 'running',
        'authorized': authorized,
        'drive_folder': FOLDER_NAME,
        'api_key_configured': bool(API_KEY)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
