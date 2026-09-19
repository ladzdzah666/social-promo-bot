import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, BrowserContext, Page
import config

class BasePoster:
    """Base class for social media posters using Playwright persistent context."""

    def __init__(self, profile_dir: Path, headless: bool = config.HEADLESS_MODE):
        self.profile_dir = Path(profile_dir)
        self.headless = headless
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None

    def start_browser(self):
        """Starts browser with persistent context."""
        self.playwright = sync_playwright().start()
        # Launch persistent context with realistic user agent and viewport
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ],
            timeout=config.BROWSER_TIMEOUT_MS
        )
        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

    def stop_browser(self):
        """Safely closes browser and playwright instance."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"[BasePoster] Warning on stop_browser: {e}")

    def random_sleep(self, min_sec=config.ACTION_DELAY_MIN, max_sec=config.ACTION_DELAY_MAX):
        """Sleeps for a random duration to mimic human pauses."""
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)

    def human_type(self, selector: str, text: str):
        """Types text with random delays between characters."""
        self.page.click(selector)
        self.random_sleep(0.5, 1.0)
        
        # For multiline or long text with emojis, Playwright's type or clipboard paste is helpful.
        # Direct typing can sometimes struggle with certain emojis on web inputs,
        # so we type in chunks or fill if complex.
        for char in text:
            self.page.keyboard.type(char, delay=random.uniform(config.TYPING_DELAY_MIN * 1000, config.TYPING_DELAY_MAX * 1000))
        self.random_sleep(0.5, 1.0)
