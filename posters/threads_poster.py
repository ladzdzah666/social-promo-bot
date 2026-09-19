import os
from pathlib import Path
from posters.base_poster import BasePoster
import config

class ThreadsPoster(BasePoster):
    """Automates posting to Threads (threads.net)."""

    def __init__(self, headless: bool = config.HEADLESS_MODE):
        super().__init__(profile_dir=config.THREADS_PROFILE_DIR, headless=headless)

    def is_logged_in(self) -> bool:
        """Checks if current session is logged into Threads."""
        self.page.goto("https://www.threads.net", wait_until="domcontentloaded")
        self.random_sleep(3, 5)

        current_url = self.page.url
        if "login" in current_url:
            return False

        # Look for create button or profile avatar
        try:
            create_btn = self.page.locator('svg[aria-label="Create"], [aria-label="New thread"], div[contenteditable="true"]')
            return create_btn.count() > 0
        except Exception:
            return False

    def post(self, caption: str, image_path: str = "") -> bool:
        """Posts a thread with optional image."""
        try:
            print("[ThreadsPoster] Navigating to https://www.threads.net ...")
            self.page.goto("https://www.threads.net", wait_until="domcontentloaded")
            self.random_sleep(4, 6)

            # Check if redirected to login
            if "login" in self.page.url:
                print("[ThreadsPoster] ERROR: Session not authenticated on Threads. Run 'python setup_accounts.py' first.")
                return False

            # Click Create / New thread button
            create_triggers = [
                'svg[aria-label="Create"]',
                'svg[aria-label="Buat"]',
                'div[role="button"]:has(svg[aria-label="Create"])',
                'span:has-text("Start a thread")',
                'span:has-text("Mulai thread...")',
                '[aria-label="New thread"]'
            ]
            
            trigger_found = False
            for selector in create_triggers:
                loc = self.page.locator(selector).first
                if loc.is_visible():
                    loc.click()
                    trigger_found = True
                    break

            self.random_sleep(2, 3)

            # Wait for text editor in composer
            editor_locators = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                'p[data-placeholder*="thread"]'
            ]
            
            editor = None
            for sel in editor_locators:
                loc = self.page.locator(sel).first
                if loc.is_visible():
                    editor = loc
                    break

            if not editor:
                print("[ThreadsPoster] Composer text input element not found.")
                return False

            editor.click()
            self.random_sleep(1, 2)

            # Type caption
            print("[ThreadsPoster] Composing post caption...")
            self.page.evaluate(
                """([text]) => {
                    const el = document.querySelector('div[contenteditable="true"][role="textbox"]') || document.querySelector('div[contenteditable="true"]');
                    if (el) {
                        el.focus();
                        document.execCommand('insertText', false, text);
                    }
                }""",
                [caption]
            )
            self.random_sleep(2, 3)

            # Upload image if provided
            if image_path and Path(image_path).exists():
                abs_img_path = str(Path(image_path).resolve())
                print(f"[ThreadsPoster] Uploading media attachment: {abs_img_path} ...")
                file_input = self.page.locator('input[type="file"][accept*="image"]').first
                if file_input:
                    file_input.set_input_files(abs_img_path)
                    print("[ThreadsPoster] Waiting for media processing...")
                    self.random_sleep(4, 7)

            # Find Post / Kirim button
            post_button = self.page.locator('div[role="button"]:has-text("Post"), div[role="button"]:has-text("Kirim")').last
            if not post_button.is_visible():
                print("[ThreadsPoster] Post button not found.")
                return False

            print("[ThreadsPoster] Dispatching post to Threads...")
            self.random_sleep(1, 2)
            post_button.click()

            # Wait for post to complete
            self.random_sleep(5, 8)
            print("[ThreadsPoster] Successfully published post to Threads.")
            return True

        except Exception as e:
            print(f"[ThreadsPoster] Failed to publish post on Threads: {e}")
            return False
