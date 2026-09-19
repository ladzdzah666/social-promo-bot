import json
import random
import time
import urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
import config

HISTORY_FILE = config.BASE_DIR / "replied_history.json"
TEMPLATES_FILE = config.BASE_DIR / "reply_templates.txt"

def load_history() -> set:
    """Loads previously replied post IDs / URLs to prevent redundant responses."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history: set):
    """Persists replied history set to JSON storage."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(history), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Engagement] Warning: Failed to persist interaction history: {e}")

def load_reply_templates() -> list:
    """Loads randomized reply copy templates from local text file."""
    if TEMPLATES_FILE.exists():
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                return lines
    return [
        "Check out our catalog at the link in bio for official warranty and discounts!",
        "Looking for premium quality with special promos? Visit our profile link to learn more.",
        "Exclusive discounts available today. Feel free to browse our bio link for details!"
    ]

def auto_reply_x(keyword: str, max_replies: int = 3, custom_templates: list = None):
    """Queries X for matching search keyword and responds to recent items."""
    templates = custom_templates if custom_templates else load_reply_templates()
    history = load_history()

    print("\n" + "-" * 56)
    print(f"[Engagement-X] Search Query : '{keyword}'")
    print(f"[Engagement-X] Max Target   : {max_replies} reply(s)")
    print("-" * 56)

    p = sync_playwright().start()
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(config.X_PROFILE_DIR),
        headless=config.HEADLESS_MODE,
        viewport={"width": 1280, "height": 800},
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    encoded_kw = urllib.parse.quote(keyword)
    search_url = f"https://x.com/search?q={encoded_kw}&f=live"

    replied_count = 0

    try:
        print(f"[Engagement-X] Querying live search feed: {search_url}")
        page.goto(search_url, wait_until="domcontentloaded")
        time.sleep(5)

        if "login" in page.url:
            print("[Engagement-X] ERROR: Session not authenticated. Run Account Setup first.")
            return

        for scroll_attempt in range(5):
            if replied_count >= max_replies:
                break

            articles = page.locator('article[data-testid="tweet"]').all()
            print(f"[Engagement-X] Detected {len(articles)} tweet items on viewport...")

            for tweet in articles:
                if replied_count >= max_replies:
                    break

                try:
                    link_elem = tweet.locator('a[href*="/status/"]').first
                    if not link_elem.count():
                        continue

                    post_url = link_elem.get_attribute("href")
                    if not post_url or post_url in history:
                        continue

                    print(f"\n[Engagement-X] Inspecting post: https://x.com{post_url}")
                    
                    tweet.scroll_into_view_if_needed()
                    time.sleep(1.5)

                    reply_btn = tweet.locator('button[data-testid="reply"]').first
                    if not reply_btn.is_visible():
                        continue

                    reply_btn.click()
                    time.sleep(2.5)

                    reply_box = page.wait_for_selector('[data-testid="tweetTextarea_0"], div[role="textbox"]', timeout=8000)
                    if not reply_box:
                        print("[Engagement-X] Reply composer did not appear. Skipping.")
                        continue

                    message = random.choice(templates)
                    summary_msg = message[:50] + "..." if len(message) > 50 else message
                    print(f"[Engagement-X] Composing response: \"{summary_msg}\"")

                    reply_box.click()
                    time.sleep(1)
                    page.evaluate(
                        """([text]) => {
                            const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('div[role="textbox"]');
                            if (el) {
                                el.focus();
                                document.execCommand('insertText', false, text);
                            }
                        }""",
                        [message]
                    )
                    time.sleep(2)

                    submit_btn = page.wait_for_selector('[data-testid="tweetButton"]', timeout=6000)
                    if submit_btn and not submit_btn.is_disabled():
                        submit_btn.click()
                        print("[Engagement-X] [OK] Reply dispatched successfully.")
                        replied_count += 1
                        history.add(post_url)
                        save_history(history)

                        delay = random.randint(30, 60)
                        print(f"[Engagement-X] Cooling down for {delay}s safety interval...")
                        time.sleep(delay)
                    else:
                        print("[Engagement-X] Submit button unavailable.")
                        page.keyboard.press("Escape")
                        time.sleep(1)

                except Exception:
                    try:
                        page.keyboard.press("Escape")
                    except Exception:
                        pass
                    continue

            page.evaluate("window.scrollBy(0, 800);")
            time.sleep(3)

    except Exception as e:
        print(f"[Engagement-X] Error during auto-reply execution: {e}")
    finally:
        print(f"\n[Engagement-X] Completed. Total {replied_count} reply(s) sent.")
        context.close()
        p.stop()

def auto_reply_threads(keyword: str, max_replies: int = 3, custom_templates: list = None):
    """Queries Threads for matching keyword and responds to recent items."""
    templates = custom_templates if custom_templates else load_reply_templates()
    history = load_history()

    print("\n" + "-" * 56)
    print(f"[Engagement-Threads] Search Query : '{keyword}'")
    print(f"[Engagement-Threads] Max Target   : {max_replies} reply(s)")
    print("-" * 56)

    p = sync_playwright().start()
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(config.THREADS_PROFILE_DIR),
        headless=config.HEADLESS_MODE,
        viewport={"width": 1280, "height": 800},
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    encoded_kw = urllib.parse.quote(keyword)
    search_url = f"https://www.threads.net/search?q={encoded_kw}&serp_type=default"

    replied_count = 0

    try:
        print(f"[Engagement-Threads] Querying search feed: {search_url}")
        page.goto(search_url, wait_until="domcontentloaded")
        time.sleep(5)

        if "login" in page.url:
            print("[Engagement-Threads] ERROR: Session not authenticated. Run Account Setup first.")
            return

        for scroll_attempt in range(5):
            if replied_count >= max_replies:
                break

            reply_buttons = page.locator('svg[aria-label="Reply"], svg[aria-label="Balas"]').all()
            print(f"[Engagement-Threads] Detected {len(reply_buttons)} actionable item(s)...")

            for btn in reply_buttons:
                if replied_count >= max_replies:
                    break

                try:
                    btn.scroll_into_view_if_needed()
                    time.sleep(1.5)
                    btn.click()
                    time.sleep(2.5)

                    editor = page.locator('div[contenteditable="true"]').first
                    if not editor.is_visible():
                        continue

                    message = random.choice(templates)
                    summary_msg = message[:50] + "..." if len(message) > 50 else message
                    print(f"[Engagement-Threads] Composing response: \"{summary_msg}\"")

                    editor.click()
                    time.sleep(1)
                    page.evaluate(
                        """([text]) => {
                            const el = document.querySelector('div[contenteditable="true"]');
                            if (el) {
                                el.focus();
                                document.execCommand('insertText', false, text);
                            }
                        }""",
                        [message]
                    )
                    time.sleep(2)

                    post_btn = page.locator('div[role="button"]:has-text("Post"), div[role="button"]:has-text("Kirim"), div[role="button"]:has-text("Balas")').last
                    if post_btn.is_visible():
                        post_btn.click()
                        print("[Engagement-Threads] [OK] Reply dispatched successfully.")
                        replied_count += 1

                        delay = random.randint(30, 60)
                        print(f"[Engagement-Threads] Cooling down for {delay}s safety interval...")
                        time.sleep(delay)
                    else:
                        page.keyboard.press("Escape")
                        time.sleep(1)

                except Exception:
                    try:
                        page.keyboard.press("Escape")
                    except Exception:
                        pass
                    continue

            page.evaluate("window.scrollBy(0, 800);")
            time.sleep(3)

    except Exception as e:
        print(f"[Engagement-Threads] Error during auto-reply execution: {e}")
    finally:
        print(f"\n[Engagement-Threads] Completed. Total {replied_count} reply(s) sent.")
        context.close()
        p.stop()
