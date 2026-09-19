import os
from pathlib import Path
from posters.base_poster import BasePoster
import config

class XPoster(BasePoster):
    """Automates posting to X (formerly Twitter)."""

    def __init__(self, headless: bool = config.HEADLESS_MODE):
        super().__init__(profile_dir=config.X_PROFILE_DIR, headless=headless)

    def is_logged_in(self) -> bool:
        """Checks if current session is logged into X."""
        self.page.goto("https://x.com/home", wait_until="domcontentloaded")
        self.random_sleep(3, 5)

        # If redirected to login or sign in screen
        current_url = self.page.url
        if "login" in current_url or "i/flow/login" in current_url:
            return False

        # Look for typical logged-in elements (e.g. tweetTextarea or side navigation)
        try:
            compose_box = self.page.locator('[data-testid="tweetTextarea_0"], [data-testid="SideNav_NewTweet_Button"]')
            return compose_box.count() > 0
        except Exception:
            return False

    def post(self, caption: str, image_path: str = "") -> bool:
        """Posts a tweet with optional image."""
        try:
            print("[XPoster] Navigating to https://x.com/compose/post ...")
            self.page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
            self.random_sleep(3, 5)

            # Check if redirected to login
            if "login" in self.page.url:
                print("[XPoster] ERROR: Session not authenticated on X. Run 'python setup_accounts.py' first.")
                return False

            # Wait for tweet input textarea
            tweet_box = self.page.wait_for_selector(
                '[data-testid="tweetTextarea_0"], div[role="textbox"]',
                timeout=15000
            )
            if not tweet_box:
                print("[XPoster] Composer input element not found.")
                return False

            # Click and focus
            tweet_box.click()
            self.random_sleep(1, 2)

            # Insert caption (using page.keyboard to simulate typing or clipboard paste)
            print("[XPoster] Composing post caption...")
            self.page.evaluate(
                """([text]) => {
                    const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('div[role="textbox"]');
                    if (el) {
                        el.focus();
                        document.execCommand('insertText', false, text);
                    }
                }""",
                [caption]
            )
            self.random_sleep(2, 3)

            # If image is specified, upload it
            if image_path and Path(image_path).exists():
                abs_img_path = str(Path(image_path).resolve())
                print(f"[XPoster] Uploading media attachment: {abs_img_path} ...")
                file_input = self.page.wait_for_selector('input[data-testid="fileInput"]', timeout=10000)
                if file_input:
                    file_input.set_input_files(abs_img_path)
                    print("[XPoster] Waiting for media processing...")
                    self.random_sleep(3, 6)

            # Click Post / Tweet button
            post_button = self.page.wait_for_selector(
                '[data-testid="tweetButton"], [data-testid="tweetButtonInline"]',
                timeout=10000
            )
            
            if not post_button:
                print("[XPoster] Post button not found.")
                return False

            # Check if post button is disabled
            is_disabled = post_button.get_attribute("aria-disabled") == "true" or post_button.is_disabled()
            if is_disabled:
                print("[XPoster] Post button is disabled (character limit exceeded or validation error).")
                return False

            print("[XPoster] Dispatching post...")
            self.random_sleep(1, 2)
            post_button.click()

            # Wait for upload / publish to complete
            self.random_sleep(5, 8)
            print("[XPoster] Successfully published post to X.")
            return True

        except Exception as e:
            print(f"[XPoster] Failed to publish post on X: {e}")
            return False
