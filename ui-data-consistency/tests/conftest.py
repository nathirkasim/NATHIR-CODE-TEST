from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from framework.browser import BrowserSession
from framework.config import load_config, page_specs
from framework.runner import ConsistencyRunner

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@pytest.fixture(scope="session")
def configured() -> bool:
    return bool(os.getenv("BASE_URL"))


@pytest.fixture(scope="session")
def config() -> dict:
    return load_config(ROOT / "config" / "pages.yaml")


@pytest.fixture(scope="session")
def pages(config: dict):
    return page_specs(config)


@pytest.fixture(scope="session")
def runner(configured: bool):
    if not configured:
        pytest.skip("Set BASE_URL in .env to run browser consistency tests.")
    session = BrowserSession(ROOT)
    session.start()
    value = ConsistencyRunner(ROOT, session)
    try:
        yield value
    finally:
        value.finalize()
        session.close()
