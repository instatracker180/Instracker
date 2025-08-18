import instaloader
import smtplib
import time
import os
from tqdm import tqdm
from email.message import EmailMessage

# --- CONFIGURATION ---

# Instagram bot account details (read from environment variables)
BOT_USERNAME = os.environ['BOT_USERNAME']
SESSION_FILE = f"{BOT_USERNAME}.session"

# List of Instagram usernames to track
TARGET_USERNAMES = ["talkcashplz", "_wyntergrace_", "bigmansxo", "radnov.01"] # Replace with your targets

# Email configuration (read from environment variables)
SENDER_EMAIL = os.environ['SENDER_EMAIL']
SENDER_PASSWORD = os.environ['SENDER_PASSWORD']
RECEIVER_EMAIL = os.environ['RECEIVER_EMAIL']

# Timing configuration (in seconds)
DELAY_BETWEEN_ACCOUNTS = 30 # Delay is still used between checking accounts

# --- END OF CONFIGURATION ---


def send_summary_email(changes):
    """Sends a single email summarizing all detected follower changes."""
    if not changes:
        return

    msg = EmailMessage()
    msg['Subject'] = f"Instagram Follower Alert: {len(changes)} account(s) changed"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    body = "Follower counts have changed for the following accounts:\n\n"
    for change in changes:
        body += (
            f"👤 Account: {change['username']}\n"
            f"   - Previous: {change['old_count']}\n"
            f"   - Current:  {change['new_count']}\n\n"
        )
    
    msg.set_content(body)

    try:
        print("📥 Sending summary email...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def check_followers(loader):
    """Checks followers for all target users and returns a list of changes."""
    changes_found = []
    
    pbar = tqdm(TARGET_USERNAMES, desc="Initializing...")

    for username in pbar:
        try:
            pbar.set_description(f"🔎 Checking {username}")
            
            profile = instaloader.Profile.from_username(loader.context, username)
            current_followers = profile.followers

            count_file = f"{username}_followers.txt"
            last_followers = 0
            if os.path.exists(count_file):
                with open(count_file, 'r') as f:
                    try:
                        last_followers = int(f.read())
                    except ValueError:
                        last_followers = 0

            if last_followers != 0 and current_followers != last_followers:
                changes_found.append({
                    "username": username,
                    "old_count": last_followers,
                    "new_count": current_followers
                })
            
            with open(count_file, 'w') as f:
                f.write(str(current_followers))

            pbar.set_description(f"⏱️ Waiting for {DELAY_BETWEEN_ACCOUNTS}s after {username}")
            time.sleep(DELAY_BETWEEN_ACCOUNTS)

        except Exception as e:
            pbar.set_description(f"❌ Error on {username}")
            print(f"\nAn error occurred for {username}: {e}")
            time.sleep(DELAY_BETWEEN_ACCOUNTS)

    return changes_found

# --- Main Execution Block (No While Loop) ---
if __name__ == "__main__":
    L = instaloader.Instaloader()
    try:
        L.load_session_from_file(BOT_USERNAME, SESSION_FILE)
        print(f"✅ Session for '{BOT_USERNAME}' loaded successfully.")
    except FileNotFoundError:
        # If the session file doesn't exist, run login.py to create it
        print(f"❌ Session file not found. Running login.py to create a new one.")
        # This requires BOT_PASSWORD to be available as a secret
        os.system('python login.py')
        # Load the newly created session
        L.load_session_from_file(BOT_USERNAME, SESSION_FILE)

    # Run the check once
    changes = check_followers(L)
    
    if changes:
        send_summary_email(changes)
    else:
        print("✅ No changes detected in this cycle.")

    print("\n✅ Script finished.")
