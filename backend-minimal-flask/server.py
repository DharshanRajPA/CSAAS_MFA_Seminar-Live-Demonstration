"""
Flask server for MFA demo
Provides REST API endpoints for authentication and MFA flows
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from auth_core import AuthCore

# Get the base directory (backend-minimal-flask)
BASE_DIR = Path(__file__).parent
# Get frontend directory (parent directory + frontend)
FRONTEND_DIR = BASE_DIR.parent / 'frontend'

app = Flask(__name__, static_folder=str(FRONTEND_DIR))
CORS(app)

# Initialize auth core
auth = AuthCore()

@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    return send_from_directory(str(FRONTEND_DIR), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    return send_from_directory(str(FRONTEND_DIR), filename)

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        email = data['email']
        password = data['password']
        
        # Basic validation
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        result = auth.register_user(email, password)
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        print(f"Registration endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        email = data['email']
        password = data['password']
        
        result = auth.login_user(email, password)
        if 'error' in result:
            return jsonify(result), 401
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Login endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/mfa/enable', methods=['POST'])
def enable_mfa():
    """Enable TOTP MFA for user"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        payload = auth.verify_jwt(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload['user_id']
        result = auth.enable_totp(user_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"MFA enable endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/mfa/totp/verify', methods=['POST'])
def verify_totp():
    """Verify TOTP code"""
    try:
        data = request.get_json()
        if not data or 'temp_token' not in data or 'totp_code' not in data:
            return jsonify({"error": "temp_token and totp_code required"}), 400
        
        temp_token = data['temp_token']
        totp_code = data['totp_code']
        
        result = auth.verify_totp(temp_token, totp_code)
        if 'error' in result:
            return jsonify(result), 401
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"TOTP verify endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/mfa/email/send_otp', methods=['POST'])
def send_email_otp():
    """Send email OTP"""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({"error": "Email required"}), 400
        
        email = data['email']
        result = auth.send_email_otp(email)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Email OTP send endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/mfa/email/verify', methods=['POST'])
def verify_email_otp():
    """Verify email OTP"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'otp' not in data or 'temp_token' not in data:
            return jsonify({"error": "email, otp, and temp_token required"}), 400
        
        email = data['email']
        otp = data['otp']
        temp_token = data['temp_token']
        
        result = auth.verify_email_otp(email, otp, temp_token)
        if 'error' in result:
            return jsonify(result), 401
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Email OTP verify endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile (protected endpoint)"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token required"}), 401
        
        token = auth_header.split(' ')[1]
        payload = auth.verify_jwt(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload['user_id']
        result = auth.get_user_profile(user_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Profile endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment variable (Railway provides this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting MFA Demo Server...")
    print(f"Server will be available at: http://0.0.0.0:{port}")
    print(f"Frontend will be served at: http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
