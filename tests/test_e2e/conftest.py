import pytest
from playwright.sync_api import Browser, BrowserContext, Page
from pathlib import Path
import shutil
from src.config import settings
import multiprocessing
import uvicorn
import time
import signal
import subprocess
import os
import sys
from src.api.main import app

class TestServer:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.process = None
        
    def start(self):
        """Start the FastAPI server using subprocess."""
        if self.process is None:
            # Create the command to run uvicorn
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                "src.api.main:app",
                "--host", self.host,
                "--port", str(self.port)
            ]
            
            # Start the server as a subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(2)
    
    def stop(self):
        """Stop the server process."""
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None

@pytest.fixture(scope="session")
def test_server():
    """Fixture that provides an automatically managed test server."""
    server = TestServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after each test."""
    # Clean before test
    for dir_path in [settings.UPLOAD_DIR, settings.AUDIO_DIR]:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Clean after test
    for dir_path in [settings.UPLOAD_DIR, settings.AUDIO_DIR]:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

@pytest.fixture
def test_image_path() -> str:
    """Return the path to the test image."""
    return str(Path(__file__).parent.parent / "test_api" / "test_data" / "realistic_scene.jpg")

@pytest.fixture
def mobile_viewport(page: Page):
    """Configure page for mobile viewport."""
    page.set_viewport_size({"width": 375, "height": 667})
    return page

@pytest.fixture
def tablet_viewport(page: Page):
    """Configure page for tablet viewport."""
    page.set_viewport_size({"width": 768, "height": 1024})
    return page

@pytest.fixture
def desktop_viewport(page: Page):
    """Configure page for desktop viewport."""
    page.set_viewport_size({"width": 1920, "height": 1080})
    return page

@pytest.fixture
def authenticated_context(browser: Browser) -> BrowserContext:
    """Create a browser context with authentication."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        accept_downloads=True
    )
    # Add any authentication logic here if needed in the future
    return context

@pytest.fixture
def authenticated_page(authenticated_context: BrowserContext) -> Page:
    """Create a page with authentication."""
    page = authenticated_context.new_page()
    yield page
    page.close()

@pytest.fixture
def mock_slow_response(page: Page):
    """Mock slow responses for testing loading states."""
    page.route("**/process_with_narrative/", lambda route: route.continue_(timeout=5000))
    return page 