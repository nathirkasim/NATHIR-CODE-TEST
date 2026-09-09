from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, TimeoutError as PlaywrightTimeoutError, sync_playwright

LOGGER = logging.getLogger(__name__)


class BrowserSession:
    """Owns a Chromium session and optionally persists authenticated state."""

    def __init__(self, root: Path | None = None) -> None:
        load_dotenv()
        self.root = root or Path(__file__).resolve().parents[1]
        self.base_url = os.getenv("BASE_URL", "").rstrip("/")
        self.state_path = self.root / os.getenv("STORAGE_STATE", "reports/storage_state.json")
        self.headless = os.getenv("HEADLESS", "true").lower() not in {"0", "false", "no"}
        self.timeout_ms = int(os.getenv("BROWSER_TIMEOUT_MS", "15000"))
        self.network_timeout_ms = int(os.getenv("NETWORK_TIMEOUT_MS", "10000"))
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    def start(self) -> BrowserContext:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        options = {"ignore_https_errors": True}
        if self.state_path.exists():
            options["storage_state"] = str(self.state_path)
        self.context = self.browser.new_context(**options)
        self.context.set_default_timeout(self.timeout_ms)
        self.context.set_default_navigation_timeout(self.network_timeout_ms)
        return self.context

    def close(self) -> None:
        if self.context:
            self.context.storage_state(path=str(self.state_path))
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.context = self.browser = self.playwright = None

    @contextmanager
    def page(self) -> Iterator[Page]:
        if not self.context:
            raise RuntimeError("BrowserSession.start() must be called before page().")
        page = self.context.new_page()
        try:
            yield page
        except PlaywrightTimeoutError:
            LOGGER.exception("Browser timeout while visiting %s", page.url)
            raise
        finally:
            page.close()

    def url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not self.base_url:
            raise ValueError("BASE_URL must be set in .env before running browser tests.")
        return f"{self.base_url}/{path.lstrip('/')}"

    def login(self, page: Page, login_path: str | None = None, selectors: dict[str, str] | None = None) -> None:
        """Perform configurable login only when no persisted storage state exists."""
        if self.state_path.exists():
            return
        if not login_path:
            LOGGER.info("No login_path configured; continuing without login.")
            return
        username = os.getenv("USERNAME", "")
        password = os.getenv("PASSWORD", "")
        if not username or not password:
            LOGGER.info("USERNAME/PASSWORD are not configured; continuing without login.")
            return
        selectors = selectors or {}
        page.goto(self.url(login_path), wait_until="domcontentloaded")
        page.locator(selectors.get("username", 'input[name="username"], input[type="email"]')).fill(username)
        page.locator(selectors.get("password", 'input[name="password"], input[type="password"]')).fill(password)
        page.locator(selectors.get("submit", 'button[type="submit"]')).click()
        page.wait_for_load_state("networkidle")


def screenshot(page: Page, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(destination), full_page=True)
    return str(destination)
