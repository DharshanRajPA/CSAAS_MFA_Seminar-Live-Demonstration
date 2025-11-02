/**
 * Frontend JavaScript for MFA Demo
 * Handles all authentication flows and UI interactions
 */

// Global state
let currentToken = null;
let tempToken = null;
let currentUser = null;

// API base URL
const API_BASE = '';

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

function hideAllSections() {
    document.getElementById('authForm').classList.add('hidden');
    document.getElementById('mfaSection').classList.add('hidden');
    document.getElementById('mfaSetupSection').classList.add('hidden');
    document.getElementById('dashboardSection').classList.add('hidden');
    document.getElementById('emailOTPSection').classList.add('hidden');
}

function showSection(sectionId) {
    hideAllSections();
    document.getElementById(sectionId).classList.remove('hidden');
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null, token = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Authentication functions
async function register() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const result = await apiCall('/api/register', 'POST', { email, password });
        showAlert('Registration successful! You can now login.', 'success');
    } catch (error) {
        showAlert(`Registration failed: ${error.message}`, 'error');
    }
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const result = await apiCall('/api/login', 'POST', { email, password });
        
        if (result.mfa_required) {
            tempToken = result.temp_token;
            showSection('mfaSection');
            showAlert('MFA required. Please verify your identity.', 'info');
        } else {
            currentToken = result.token;
            await loadUserProfile();
            showSection('dashboardSection');
            showAlert('Login successful!', 'success');
        }
    } catch (error) {
        showAlert(`Login failed: ${error.message}`, 'error');
    }
}

async function verifyTOTP() {
    const totpCode = document.getElementById('totpCode').value;
    
    if (!totpCode || totpCode.length !== 6) {
        showAlert('Please enter a valid 6-digit TOTP code', 'error');
        return;
    }
    
    try {
        const result = await apiCall('/api/mfa/totp/verify', 'POST', {
            temp_token: tempToken,
            totp_code: totpCode
        });
        
        currentToken = result.token;
        await loadUserProfile();
        showSection('dashboardSection');
        showAlert('TOTP verification successful!', 'success');
    } catch (error) {
        showAlert(`TOTP verification failed: ${error.message}`, 'error');
    }
}

async function sendEmailOTP() {
    const email = document.getElementById('email').value;
    
    try {
        await apiCall('/api/mfa/email/send_otp', 'POST', { email });
        document.getElementById('emailOTPSection').classList.remove('hidden');
        showAlert('OTP sent! Check server console for the code (demo mode).', 'info');
    } catch (error) {
        showAlert(`Failed to send OTP: ${error.message}`, 'error');
    }
}

async function verifyEmailOTP() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('emailOTP').value;
    
    if (!otp || otp.length !== 6) {
        showAlert('Please enter a valid 6-digit OTP', 'error');
        return;
    }
    
    try {
        const result = await apiCall('/api/mfa/email/verify', 'POST', {
            email,
            otp,
            temp_token: tempToken
        });
        
        currentToken = result.token;
        await loadUserProfile();
        showSection('dashboardSection');
        showAlert('Email OTP verification successful!', 'success');
    } catch (error) {
        showAlert(`OTP verification failed: ${error.message}`, 'error');
    }
}

async function loadUserProfile() {
    try {
        const profile = await apiCall('/api/profile', 'GET', null, currentToken);
        currentUser = profile;
        displayProfile(profile);
    } catch (error) {
        showAlert(`Failed to load profile: ${error.message}`, 'error');
    }
}

function displayProfile(profile) {
    const profileInfo = document.getElementById('profileInfo');
    const mfaStatus = document.getElementById('mfaStatus');
    const mfaToggleBtn = document.getElementById('mfaToggleBtn');
    
    profileInfo.innerHTML = `
        <p><strong>Email:</strong> ${profile.email}</p>
        <p><strong>User ID:</strong> ${profile.user_id}</p>
        <p><strong>Created:</strong> ${new Date(profile.created_at).toLocaleDateString()}</p>
    `;
    
    if (profile.mfa_enabled) {
        mfaStatus.innerHTML = '<span class="status-indicator status-enabled"></span>Enabled';
        mfaToggleBtn.textContent = 'Disable MFA';
        mfaToggleBtn.className = 'btn btn-danger';
    } else {
        mfaStatus.innerHTML = '<span class="status-indicator status-disabled"></span>Disabled';
        mfaToggleBtn.textContent = 'Enable MFA';
        mfaToggleBtn.className = 'btn';
    }
}

async function toggleMFA() {
    if (currentUser.mfa_enabled) {
        // Disable MFA (simplified - in production, would need confirmation)
        showAlert('MFA disable not implemented in demo. Please contact admin.', 'info');
        return;
    }
    
    try {
        const result = await apiCall('/api/mfa/enable', 'POST', {}, currentToken);
        
        // Display QR code
        const qrImage = document.getElementById('qrImage');
        qrImage.src = `data:image/png;base64,${result.qr_png_base64}`;
        
        showSection('mfaSetupSection');
        showAlert('Scan the QR code with your authenticator app', 'info');
    } catch (error) {
        showAlert(`Failed to enable MFA: ${error.message}`, 'error');
    }
}

async function verifySetupTOTP() {
    const totpCode = document.getElementById('setupTOTPCode').value;
    
    if (!totpCode || totpCode.length !== 6) {
        showAlert('Please enter a valid 6-digit TOTP code', 'error');
        return;
    }
    
    // In a real implementation, we would verify the TOTP code here
    // For demo purposes, we'll just show success
    showAlert('MFA setup successful! Please login again to test.', 'success');
    logout();
}

function skipMFA() {
    showAlert('MFA setup skipped. You can enable it later from your profile.', 'info');
    showSection('dashboardSection');
}

function logout() {
    currentToken = null;
    tempToken = null;
    currentUser = null;
    
    // Clear form fields
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    document.getElementById('totpCode').value = '';
    document.getElementById('emailOTP').value = '';
    document.getElementById('setupTOTPCode').value = '';
    
    showSection('authForm');
    showAlert('Logged out successfully', 'success');
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    showSection('authForm');
    
    // Add enter key support for forms
    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });
    
    document.getElementById('totpCode').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            verifyTOTP();
        }
    });
    
    document.getElementById('emailOTP').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            verifyEmailOTP();
        }
    });
    
    document.getElementById('setupTOTPCode').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            verifySetupTOTP();
        }
    });
});
