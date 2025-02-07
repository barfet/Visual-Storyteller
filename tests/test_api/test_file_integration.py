import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from PIL import Image
from src.api.main import app
from tests.test_api.fixtures import realistic_image, cleanup

@pytest.fixture
def client():
    return TestClient(app)

def test_upload_valid_image(client, realistic_image):
    """Test uploading a valid image file."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("scene.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    assert "file_path" in response.json()
    assert os.path.exists(response.json()["file_path"])
    assert response.json()["file_path"].endswith(".jpg")

def test_upload_invalid_file_type(client, tmp_path):
    """Test uploading an invalid file type."""
    # Create an invalid file
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("This is not an image")
    
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "not allowed" in response.json()["detail"]

def test_upload_multiple_images(client, realistic_image):
    """Test uploading multiple images to ensure unique filenames."""
    paths = []
    
    # Upload the same image twice
    for _ in range(2):
        with open(realistic_image, "rb") as f:
            response = client.post(
                "/upload/",
                files={"file": ("scene.jpg", f, "image/jpeg")}
            )
        
        assert response.status_code == 200
        paths.append(response.json()["file_path"])
    
    # Verify paths are different
    assert len(paths) == 2
    assert paths[0] != paths[1]
    assert all(os.path.exists(path) for path in paths)

def test_upload_large_image(client, tmp_path):
    """Test uploading a large image file."""
    # Create a large image (10MB)
    large_image = tmp_path / "large.jpg"
    image = Image.new('RGB', (5000, 5000), color='red')
    image.save(large_image, quality=95)
    
    with open(large_image, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("large.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    assert "file_path" in response.json()
    assert os.path.exists(response.json()["file_path"])

def test_concurrent_uploads(client, realistic_image):
    """Test uploading multiple files concurrently."""
    paths = []
    
    # Upload multiple files sequentially (since TestClient is synchronous)
    for _ in range(5):
        with open(realistic_image, "rb") as f:
            response = client.post(
                "/upload/",
                files={"file": ("scene.jpg", f, "image/jpeg")}
            )
            assert response.status_code == 200
            paths.append(response.json()["file_path"])
    
    # Verify all uploads were successful and unique
    assert len(paths) == 5
    assert len(set(paths)) == 5  # All paths should be unique
    assert all(os.path.exists(path) for path in paths) 