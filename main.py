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
    
    # If credentials exist but are invalid, try to refresh them
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                
                # Save the refreshed token
                token_data = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                
                # Update environment variable (for next restart)
                with open(TOKEN_FILE, 'w') as token:
                    json.dump(token_data, token)
                
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                return None
        else:
            return None
    
    if not creds:
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
    
    # Check token configuration
    token_env = os.getenv('GOOGLE_TOKEN_JSON')
    token_configured = bool(token_env)
    token_valid = False
    token_error = None
    
    if token_env:
        try:
            json.loads(token_env)
            token_valid = True
        except json.JSONDecodeError as e:
            token_error = str(e)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GPT-Drive Integration Service</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; max-width: 900px; }}
            .status {{ padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .authorized {{ background: #d4edda; color: #155724; }}
            .not-authorized {{ background: #f8d7da; color: #721c24; }}
            .warning {{ background: #fff3cd; color: #856404; padding: 15px; margin: 20px 0; border-radius: 5px; }}
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
            .debug-link {{ 
                display: inline-block;
                padding: 8px 15px;
                background: #6c757d;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 5px;
                font-size: 14px;
            }}
            .debug-link:hover {{ background: #5a6268; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            .check {{ color: #28a745; }}
            .cross {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <h1>GPT-Drive Integration Service</h1>
        <div class="status {'authorized' if authorized else 'not-authorized'}">
            <h2>Status: {'✓ Authorized' if authorized else '✗ Not Authorized'}</h2>
            <p>Drive API: {'Connected' if authorized else 'Not Connected'}</p>
        </div>
        
        {'<p style="color: #28a745; font-weight: bold;">✓ Service is ready to receive requests from your GPT!</p>' if authorized else ''}
        
        {f'''<div class="warning">
            <h3>⚠️ Configuration Issue Detected</h3>
            <p><strong>Token Status:</strong></p>
            <ul>
                <li>GOOGLE_TOKEN_JSON configured: {'✓' if token_configured else '✗'}</li>
                <li>Token JSON valid: {'✓' if token_valid else '✗' if token_configured else 'N/A'}</li>
                {f'<li style="color: #dc3545;">Error: {token_error}</li>' if token_error else ''}
            </ul>
            <p><strong>To fix:</strong></p>
            <ol>
                <li>Click "Authorize with Google Drive" below</li>
                <li>Complete authorization and copy the SINGLE-LINE token</li>
                <li>Add to Railway as GOOGLE_TOKEN_JSON variable</li>
                <li>Wait for redeploy and refresh this page</li>
            </ol>
            <p><a href="/debug" class="debug-link">View Debug Info</a></p>
        </div>''' if not authorized else ''}
        
        {'<a href="/authorize" class="button">Authorize with Google Drive</a>' if not authorized else ''}
        
        <h3>Configuration</h3>
        <table>
            <tr>
                <th>Setting</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Target Folder</td>
                <td>{FOLDER_NAME}</td>
                <td class="check">✓</td>
            </tr>
            <tr>
                <td>API Key</td>
                <td>{'Configured' if API_KEY else 'Not Set'}</td>
                <td class="{'check' if API_KEY else 'cross'}">{'✓' if API_KEY else '✗'}</td>
            </tr>
            <tr>
                <td>Redirect URI</td>
                <td>{REDIRECT_URI}</td>
                <td class="check">✓</td>
            </tr>
            <tr>
                <td>Google Token</td>
                <td>{'Valid' if token_valid else 'Invalid' if token_configured else 'Not Set'}</td>
                <td class="{'check' if token_valid else 'cross'}">{'✓' if token_valid else '✗'}</td>
            </tr>
        </table>
        
        <h3>Endpoints</h3>
        <ul>
            <li><strong>POST /save-content</strong> - Save content to Drive</li>
            <li><strong>GET /authorize</strong> - Start OAuth flow</li>
            <li><strong>GET /health</strong> - Health check</li>
            <li><strong>GET /debug</strong> - Debug information</li>
        </ul>
        
        <p style="margin-top: 30px;">
            <a href="/health" class="debug-link">Health Check</a>
            <a href="/debug" class="debug-link">Debug Info</a>
        </p>
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
        
        # Create single-line JSON for easy copying
        single_line_json = json.dumps(token_data, separators=(',', ':'))
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; max-width: 1000px; }}
                .success {{ background: #d4edda; padding: 20px; border-radius: 5px; color: #155724; margin-bottom: 30px; }}
                .token-box {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border: 2px solid #007bff; 
                    border-radius: 5px; 
                    margin: 20px 0;
                    font-family: monospace;
                    font-size: 12px;
                    overflow-x: auto;
                    word-break: break-all;
                }}
                .warning {{ background: #fff3cd; padding: 20px; border-radius: 5px; color: #856404; margin: 20px 0; }}
                .step {{ background: #e7f3ff; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
                .copy-btn {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 10px 20px; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer;
                    font-size: 14px;
                    margin: 10px 0;
                }}
                .copy-btn:hover {{ background: #0056b3; }}
                .important {{ color: #721c24; font-weight: bold; }}
            </style>
            <script>
                function copyToken() {{
                    const tokenText = document.getElementById('tokenText').innerText;
                    navigator.clipboard.writeText(tokenText).then(() => {{
                        const btn = document.getElementById('copyBtn');
                        btn.innerText = '✓ Copied!';
                        setTimeout(() => {{ btn.innerText = 'Copy Token to Clipboard'; }}, 2000);
                    }});
                }}
            </script>
        </head>
        <body>
            <div class="success">
                <h1>✓ Authorization Successful!</h1>
                <p>Your Google Drive is now connected.</p>
            </div>
            
            <div class="warning">
                <h2>⚠️ IMPORTANT: Final Step Required</h2>
                <p class="important">The authorization will NOT persist until you complete this step!</p>
                
                <div class="step">
                    <h3>Step 1: Copy the Token (Single Line JSON)</h3>
                    <p>Click the button below to copy the token:</p>
                    <button id="copyBtn" class="copy-btn" onclick="copyToken()">Copy Token to Clipboard</button>
                    <div class="token-box" id="tokenText">{single_line_json}</div>
                    <p><strong>Note:</strong> This is a SINGLE LINE (no line breaks). It's ready to paste directly into Railway.</p>
                </div>
                
                <div class="step">
                    <h3>Step 2: Add to Railway Environment Variables</h3>
                    <ol>
                        <li>Go to your <strong>Railway dashboard</strong></li>
                        <li>Click on your service</li>
                        <li>Go to <strong>Variables</strong> tab</li>
                        <li>Look for <strong>GOOGLE_TOKEN_JSON</strong> variable:
                            <ul>
                                <li>If it exists: Click the three dots → <strong>Edit</strong></li>
                                <li>If it doesn't exist: Click <strong>New Variable</strong></li>
                            </ul>
                        </li>
                        <li>Variable name: <code>GOOGLE_TOKEN_JSON</code></li>
                        <li>Paste the token you just copied (Ctrl+V or Cmd+V)</li>
                        <li>Click <strong>Add</strong> or <strong>Update</strong></li>
                    </ol>
                </div>
                
                <div class="step">
                    <h3>Step 3: Verify After Redeploy</h3>
                    <p>Railway will automatically redeploy (takes 1-2 minutes).</p>
                    <p>After redeployment:</p>
                    <ol>
                        <li>Visit: <a href="/">Homepage</a></li>
                        <li>Status should show: <strong>✓ Authorized</strong></li>
                        <li>Or check: <a href="/debug">/debug endpoint</a> (should show token_json_valid: true)</li>
                    </ol>
                </div>
                
                <div class="step">
                    <h3>Common Issues</h3>
                    <p><strong>If still showing "Not Authorized" after redeployment:</strong></p>
                    <ul>
                        <li>Make sure you copied the ENTIRE single-line JSON above</li>
                        <li>Check there are NO extra spaces before or after the JSON in Railway</li>
                        <li>Verify the variable name is exactly: <code>GOOGLE_TOKEN_JSON</code></li>
                        <li>Check <a href="/debug">/debug</a> to see if the token is valid</li>
                        <li>If debug shows "token_json_valid: false", delete the variable and try again</li>
                    </ul>
                </div>
            </div>
            
            <p style="margin-top: 30px;"><a href="/">← Return to Home</a></p>
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
        folder_name = data.get('folder_name', FOLDER_NAME)  # Use custom folder or default
        
        if not content or not filename:
            return jsonify({'error': 'Missing content or filename'}), 400
        
        # Initialize Drive service
        service = get_drive_service()
        if not service:
            return jsonify({
                'error': 'Not authorized with Google Drive',
                'message': 'Please visit the /authorize endpoint to connect your Google Drive'
            }), 401
        
        # Get or create folder (using custom folder name if provided)
        folder_id = get_or_create_folder(service, folder_name)
        
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
            'folder': folder_name,
            'message': f'Successfully saved to Google Drive'
        })
    
    except Exception as e:
        app.logger.error(f"Error saving to Drive: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-auth', methods=['POST', 'GET'])
def test_auth():
    """Test endpoint to diagnose authentication issues"""
    
    # Get all headers
    headers_dict = dict(request.headers)
    
    # Get the API key from header
    received_key = request.headers.get('X-API-Key', 'NOT_PRESENT')
    
    # Get expected key from environment
    expected_key = API_KEY
    
    # Check if they match
    keys_match = received_key == expected_key
    
    return jsonify({
        'authentication_test': {
            'received_api_key_length': len(received_key) if received_key != 'NOT_PRESENT' else 0,
            'expected_api_key_length': len(expected_key) if expected_key else 0,
            'received_key_first_5': received_key[:5] if received_key != 'NOT_PRESENT' else 'N/A',
            'expected_key_first_5': expected_key[:5] if expected_key else 'N/A',
            'received_key_last_5': received_key[-5:] if received_key != 'NOT_PRESENT' else 'N/A',
            'expected_key_last_5': expected_key[-5:] if expected_key else 'N/A',
            'keys_match': keys_match,
            'api_key_configured_in_env': bool(expected_key),
            'x_api_key_header_present': 'X-API-Key' in headers_dict,
        },
        'all_headers': {k: v for k, v in headers_dict.items() if 'api' in k.lower() or 'auth' in k.lower()},
        'message': 'Match!' if keys_match else 'Keys do not match'
    })

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

@app.route('/debug')
def debug():
    """Debug endpoint to check environment configuration"""
    token_env = os.getenv('GOOGLE_TOKEN_JSON')
    creds_env = os.getenv('GOOGLE_CREDENTIALS_JSON')
    
    debug_info = {
        'token_json_set': bool(token_env),
        'token_json_length': len(token_env) if token_env else 0,
        'credentials_json_set': bool(creds_env),
        'redirect_uri': REDIRECT_URI,
        'drive_folder': FOLDER_NAME,
        'api_key_set': bool(API_KEY),
    }
    
    # Try to parse token JSON
    if token_env:
        try:
            token_data = json.loads(token_env)
            debug_info['token_json_valid'] = True
            debug_info['token_json_keys'] = list(token_data.keys())
            debug_info['has_refresh_token'] = 'refresh_token' in token_data
            
            # Try to create credentials object
            try:
                from google.auth.transport.requests import Request
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
                
                debug_info['credentials_created'] = True
                debug_info['credentials_valid'] = creds.valid
                debug_info['credentials_expired'] = creds.expired if hasattr(creds, 'expired') else None
                debug_info['has_token'] = bool(creds.token)
                debug_info['has_refresh_token_obj'] = bool(creds.refresh_token)
                
                # Try to refresh if expired
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        debug_info['refresh_attempted'] = True
                        debug_info['refresh_successful'] = True
                        debug_info['credentials_valid_after_refresh'] = creds.valid
                    except Exception as e:
                        debug_info['refresh_attempted'] = True
                        debug_info['refresh_successful'] = False
                        debug_info['refresh_error'] = str(e)
                
            except Exception as e:
                debug_info['credentials_created'] = False
                debug_info['credentials_error'] = str(e)
                
        except json.JSONDecodeError as e:
            debug_info['token_json_valid'] = False
            debug_info['token_json_error'] = str(e)
            debug_info['token_json_preview'] = token_env[:100] + '...' if len(token_env) > 100 else token_env
    
    # Check if service can be initialized
    service = get_drive_service()
    debug_info['service_initialized'] = service is not None
    
    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
