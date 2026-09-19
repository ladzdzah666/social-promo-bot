"""Initial account session initialization for X and Threads.
Executes an interactive browser session to persist cookies and authentication profiles locally.
"""

import sys
import time
from playwright.sync_api import sync_playwright
import config

def setup_platform(platform_name: str, url: str, profile_dir):
    print("\n" + "=" * 60)
    print(f"  AUTHENTICATION SETUP: {platform_name.upper()}")
    print("=" * 60)
    print(f"Opening browser context at: {url}")
    print("Instructions:")
    print("  1. Enter your account credentials (username/email and password).")
    print("  2. Complete 2FA verification or captcha if prompted.")
    print("  3. Ensure you have reached the main feed / home screen.")
    print("-" * 60)

    p = sync_playwright().start()
    browser = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=False,
        viewport={"width": 1280, "height": 800},
        args=["--start-maximized"]
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto(url)

    input("\n[ACTION REQUIRED] Once signed in and the home feed has loaded, press [ENTER] here to persist session...\n")

    print(f"[INFO] Persisting browser session for {platform_name}...")
    time.sleep(2)
    browser.close()
    p.stop()
    print(f"[OK] Session successfully saved to: {profile_dir}\n")

def main():
    print("=" * 60)
    print("   SOCIAL MEDIA BOT ACCOUNT SETUP (X & THREADS)")
    print("=" * 60)
    print("Select an account to configure:")
    print("  1. X (formerly Twitter) only")
    print("  2. Threads only")
    print("  3. Both platforms (sequential)")
    print("  0. Cancel")

    choice = input("\nEnter selection (1/2/3/0): ").strip()

    if choice == "1":
        setup_platform("X (Twitter)", "https://x.com/login", config.X_PROFILE_DIR)
    elif choice == "2":
        setup_platform("Threads", "https://www.threads.net/login", config.THREADS_PROFILE_DIR)
    elif choice == "3":
        setup_platform("X (Twitter)", "https://x.com/login", config.X_PROFILE_DIR)
        setup_platform("Threads", "https://www.threads.net/login", config.THREADS_PROFILE_DIR)
    else:
        print("[INFO] Setup canceled.")

if __name__ == "__main__":
    main()
