import pytest
import os
import shutil
from src.config import settings

pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session", autouse=True)
def session_cleanup():
    """Clean up test files at the start of test session."""
    # Clean up at session start
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    if os.path.exists(settings.AUDIO_DIR):
        shutil.rmtree(settings.AUDIO_DIR)
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    yield

@pytest.fixture(autouse=True)
def test_cleanup():
    """Clean up test files after each test."""
    yield
    
    # Clean up after test
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    if os.path.exists(settings.AUDIO_DIR):
        shutil.rmtree(settings.AUDIO_DIR)
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)

@pytest.fixture(scope="session")
def event_loop_policy():
    """Return an event loop policy for the test session."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
def realistic_image(tmp_path):
    """Create a realistic test image."""
    from PIL import Image
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_path = tmp_path / "test_scene.jpg"
    img.save(img_path)
    
    return str(img_path) 