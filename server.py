from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Configuration - TOGGLE THESE TO TEST DIFFERENT SCENARIOS
ENABLE_RATE_LIMITING = False  # Set to True to enable rate limiting
ENABLE_ACCOUNT_LOCKOUT = True  # Set to True to enable account lockout
RATE_LIMIT = "10 per minute"  # Adjust rate limit
LOCKOUT_THRESHOLD = 5  # Failed attempts before lockout
LOCKOUT_DURATION = 300  # Lockout duration in seconds (5 minutes)

# Mock user database
USERS = {
    "admin": "password123",
    "user1": "qwerty",
    "testuser": "letmein"
}

# Track failed attempts and lockouts
failed_attempts = {}
locked_accounts = {}

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[]
)

def is_account_locked(username):
    """Check if account is currently locked"""
    if username in locked_accounts:
        lock_time = locked_accounts[username]
        if datetime.now() < lock_time:
            return True
        else:
            # Lock expired, remove it
            del locked_accounts[username]
            failed_attempts[username] = 0
    return False

def record_failed_attempt(username):
    """Record failed login attempt and check for lockout"""
    if username not in failed_attempts:
        failed_attempts[username] = 0
    
    failed_attempts[username] += 1
    
    if ENABLE_ACCOUNT_LOCKOUT and failed_attempts[username] >= LOCKOUT_THRESHOLD:
        locked_accounts[username] = datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
        print(f"🔒 ACCOUNT LOCKED: {username} for {LOCKOUT_DURATION} seconds")
        return True
    return False

def record_successful_attempt(username):
    """Reset failed attempts on successful login"""
    if username in failed_attempts:
        failed_attempts[username] = 0
    if username in locked_accounts:
        del locked_accounts[username]

@app.route('/')
def index():
    """Server status page"""
    return jsonify({
        "status": "running",
        "security_features": {
            "rate_limiting": ENABLE_RATE_LIMITING,
            "account_lockout": ENABLE_ACCOUNT_LOCKOUT,
            "rate_limit": RATE_LIMIT if ENABLE_RATE_LIMITING else "disabled",
            "lockout_threshold": LOCKOUT_THRESHOLD if ENABLE_ACCOUNT_LOCKOUT else "disabled"
        }
    })

@app.route('/login', methods=['POST'])
@limiter.limit(RATE_LIMIT if ENABLE_RATE_LIMITING else "1000000 per hour")
def login():
    """Mock login endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "error": "Missing credentials"}), 400
    
    username = data['username']
    password = data['password']
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if account is locked
    if ENABLE_ACCOUNT_LOCKOUT and is_account_locked(username):
        remaining = (locked_accounts[username] - datetime.now()).seconds
        print(f"❌ [{timestamp}] LOCKED ACCOUNT: {username} - {remaining}s remaining")
        return jsonify({
            "success": False, 
            "error": "Account locked",
            "remaining_lockout": remaining
        }), 403
    
    # Check credentials
    if username in USERS and USERS[username] == password:
        record_successful_attempt(username)
        print(f"✅ [{timestamp}] SUCCESS: {username}")
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        just_locked = record_failed_attempt(username)
        if just_locked:
            print(f"❌ [{timestamp}] FAILED: {username} / {password} - ACCOUNT NOW LOCKED")
        else:
            attempts = failed_attempts.get(username, 0)
            print(f"❌ [{timestamp}] FAILED: {username} / {password} - Attempt #{attempts}")
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/stats')
def stats():
    """Get current statistics"""
    return jsonify({
        "failed_attempts": failed_attempts,
        "locked_accounts": {
            username: (lock_time - datetime.now()).seconds 
            for username, lock_time in locked_accounts.items()
            if datetime.now() < lock_time
        }
    })

@app.route('/reset')
def reset():
    """Reset all tracking (for testing)"""
    failed_attempts.clear()
    locked_accounts.clear()
    print("🔄 Stats reset")
    return jsonify({"message": "Stats reset successfully"})

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 BRUTE-FORCE LOGIN SIMULATOR - SERVER")
    print("=" * 60)
    print(f"Rate Limiting: {'✅ ENABLED' if ENABLE_RATE_LIMITING else '❌ DISABLED'}")
    print(f"Account Lockout: {'✅ ENABLED' if ENABLE_ACCOUNT_LOCKOUT else '❌ DISABLED'}")
    if ENABLE_RATE_LIMITING:
        print(f"Rate Limit: {RATE_LIMIT}")
    if ENABLE_ACCOUNT_LOCKOUT:
        print(f"Lockout: {LOCKOUT_THRESHOLD} attempts, {LOCKOUT_DURATION}s duration")
    print("=" * 60)
    print("\n🎯 Target Accounts:")
    for username in USERS.keys():
        print(f"   - {username}")
    print("\n🚀 Server starting on http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=False, port=5000)