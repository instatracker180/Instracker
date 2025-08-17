import instaloader
import os

# Create an instance of Instaloader
L = instaloader.Instaloader()

# --- CONFIGURATION ---
# Read credentials securely from environment variables
BOT_USERNAME = os.environ['BOT_USERNAME']
BOT_PASSWORD = os.environ['BOT_PASSWORD']

SESSION_FILE = f"{BOT_USERNAME}.session"

print("Attempting to log in...")

try:
    # Try to log in with the provided credentials
    L.login(BOT_USERNAME, BOT_PASSWORD)
    # Save the session to the file
    L.save_session_to_file(SESSION_FILE)
    print(f"Login successful! Session saved to {SESSION_FILE}")
except Exception as e:
    print(f"An error occurred during login: {e}")
