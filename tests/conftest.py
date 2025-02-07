import pytest
import os
import shutil

pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop_policy():
    """Return an event loop policy for the test session."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
def cleanup():
    """Clean up test files after each test."""
    yield
    # Clean up uploaded files
    if os.path.exists("data/sample_images"):
        shutil.rmtree("data/sample_images")
    os.makedirs("data/sample_images", exist_ok=True)
    
    # Clean up audio files
    if os.path.exists("data/audio"):
        shutil.rmtree("data/audio")
    os.makedirs("data/audio", exist_ok=True)

@pytest.fixture
def realistic_image(tmp_path):
    """Create a realistic test image."""
    from PIL import Image
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_path = tmp_path / "test_scene.jpg"
    img.save(img_path)
    
    return str(img_path) 