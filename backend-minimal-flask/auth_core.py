"""
Core authentication business logic for MFA demo
Handles registration, login, TOTP, and email OTP flows
"""
import sqlite3
import bcrypt
import pyotp
import qrcode
import io
import base64
import jwt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# JWT secret for demo (in production, use environment variable)
JWT_SECRET = "demo_secret_key_change_in_production"
JWT_ALGORITHM = "HS256"

class AuthCore:
    def __init__(self, db_path: str = "auth_demo.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                totp_secret TEXT,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # OTPs table for email OTP storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                otp_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                type TEXT DEFAULT 'email',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_jwt(self, user_id: int, email: str, expires_minutes: int = 15) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(minutes=expires_minutes)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return {"error": "User already exists"}
            
            # Hash password and insert user
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"User registered: {email}")
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            print(f"Registration error: {e}")
            return {"error": "Registration failed"}
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return token or MFA requirement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute(
                "SELECT id, password_hash, mfa_enabled FROM users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"error": "Invalid credentials"}
            
            user_id, password_hash, mfa_enabled = user
            
            # Verify password
            if not self.verify_password(password, password_hash):
                conn.close()
                return {"error": "Invalid credentials"}
            
            conn.close()
            
            # If MFA is enabled, return temp token for MFA verification
            if mfa_enabled:
                temp_token = self.generate_jwt(user_id, email, expires_minutes=5)
                print(f"Login attempt for {email} - MFA required")
                return {
                    "mfa_required": True,
                    "temp_token": temp_token
                }
            else:
                # Direct login without MFA
                token = self.generate_jwt(user_id, email)
                print(f"Login successful for {email}")
                return {"token": token}
                
        except Exception as e:
            print(f"Login error: {e}")
            return {"error": "Login failed"}
    
    def enable_totp(self, user_id: int) -> Dict[str, Any]:
        """Enable TOTP for user and return QR code"""
        try:
            # Generate TOTP secret
            totp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(totp_secret)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp.provisioning_uri(
                name="MFA Demo",
                issuer_name="MFA Demo App"
            ))
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Store secret in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET totp_secret = ?, mfa_enabled = TRUE WHERE id = ?",
                (totp_secret, user_id)
            )
            conn.commit()
            conn.close()
            
            print(f"TOTP enabled for user {user_id}")
            return {
                "qr_png_base64": qr_base64,
                "secret": totp_secret
            }
            
        except Exception as e:
            print(f"TOTP enable error: {e}")
            return {"error": "Failed to enable TOTP"}
    
    def verify_totp(self, temp_token: str, totp_code: str) -> Dict[str, Any]:
        """Verify TOTP code and return final token"""
        try:
            # Verify temp token
            payload = self.verify_jwt(temp_token)
            if not payload:
                return {"error": "Invalid or expired temp token"}
            
            user_id = payload['user_id']
            email = payload['email']
            
            # Get user's TOTP secret
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT totp_secret FROM users WHERE id = ?",
                (user_id,)
            )
            user = cursor.fetchone()
            conn.close()
            
            if not user or not user[0]:
                return {"error": "TOTP not enabled for user"}
            
            totp_secret = user[0]
            totp = pyotp.TOTP(totp_secret)
            
            # Verify TOTP code (allow 1-step window for clock drift)
            if totp.verify(totp_code, valid_window=1):
                # Generate final token
                token = self.generate_jwt(user_id, email)
                print(f"TOTP verification successful for {email}")
                return {"token": token}
            else:
                return {"error": "Invalid TOTP code"}
                
        except Exception as e:
            print(f"TOTP verification error: {e}")
            return {"error": "TOTP verification failed"}
    
    def send_email_otp(self, email: str) -> Dict[str, Any]:
        """Send email OTP (demo: print to console)"""
        try:
            # Get user
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {"error": "User not found"}
            
            user_id = user[0]
            
            # Generate OTP
            otp_code = str(secrets.randbelow(900000) + 100000)  # 6-digit code
            otp_hash = self.hash_password(otp_code)
            
            # Store OTP with 5-minute expiry
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            cursor.execute(
                "INSERT INTO otps (user_id, otp_hash, expires_at) VALUES (?, ?, ?)",
                (user_id, otp_hash, expires_at)
            )
            conn.commit()
            conn.close()
            
            # Print OTP to console for demo
            print(f"EMAIL OTP for {email}: {otp_code}")
            print("(In production, this would be sent via SMTP)")
            
            return {"success": True, "message": "OTP sent to console for demo"}
            
        except Exception as e:
            print(f"Email OTP send error: {e}")
            return {"error": "Failed to send OTP"}
    
    def verify_email_otp(self, email: str, otp: str, temp_token: str) -> Dict[str, Any]:
        """Verify email OTP and return final token"""
        try:
            # Verify temp token
            payload = self.verify_jwt(temp_token)
            if not payload:
                return {"error": "Invalid or expired temp token"}
            
            user_id = payload['user_id']
            
            # Get and verify OTP
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT otp_hash FROM otps WHERE user_id = ? AND expires_at > ? ORDER BY id DESC LIMIT 1",
                (user_id, datetime.utcnow())
            )
            otp_record = cursor.fetchone()
            
            if not otp_record:
                conn.close()
                return {"error": "No valid OTP found"}
            
            otp_hash = otp_record[0]
            
            # Verify OTP
            if not self.verify_password(otp, otp_hash):
                conn.close()
                return {"error": "Invalid OTP"}
            
            # Clean up used OTP
            cursor.execute("DELETE FROM otps WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            # Generate final token
            token = self.generate_jwt(user_id, email)
            print(f"Email OTP verification successful for {email}")
            return {"token": token}
            
        except Exception as e:
            print(f"Email OTP verification error: {e}")
            return {"error": "OTP verification failed"}
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email, mfa_enabled, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return {"error": "User not found"}
            
            email, mfa_enabled, created_at = user
            return {
                "user_id": user_id,
                "email": email,
                "mfa_enabled": bool(mfa_enabled),
                "created_at": created_at
            }
            
        except Exception as e:
            print(f"Profile fetch error: {e}")
            return {"error": "Failed to fetch profile"}
