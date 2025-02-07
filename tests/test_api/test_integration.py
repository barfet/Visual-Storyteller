import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from PIL import Image
import numpy as np
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_image(tmp_path):
    # Create a sample image for testing
    image_path = tmp_path / "test.jpg"
    image = Image.new('RGB', (100, 100), color='red')
    image.save(image_path)
    return image_path

@pytest.fixture
def realistic_image(tmp_path):
    # Create a more realistic image for testing captioning
    # Create a simple scene with a blue sky and green ground
    image = Image.new('RGB', (224, 224))
    pixels = np.array(image)
    
    # Blue sky (top half)
    pixels[:112, :] = [135, 206, 235]  # Sky blue
    # Green ground (bottom half)
    pixels[112:, :] = [34, 139, 34]    # Forest green
    
    image = Image.fromarray(pixels.astype('uint8'))
    image_path = tmp_path / "scene.jpg"
    image.save(image_path, quality=95)
    return image_path

@pytest.fixture(autouse=True)
def cleanup():
    # Setup: ensure the upload directory exists
    os.makedirs("data/sample_images", exist_ok=True)
    
    yield
    
    # Cleanup: remove all test files after each test
    for file in Path("data/sample_images").glob("*"):
        if file.is_file():
            file.unlink()

def test_upload_valid_image(client, sample_image):
    # Test uploading a valid image file
    with open(sample_image, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    assert "file_path" in response.json()
    assert os.path.exists(response.json()["file_path"])
    assert response.json()["file_path"].endswith(".jpg")

def test_upload_invalid_file_type(client, tmp_path):
    # Create an invalid file
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("This is not an image")
    
    # Test uploading an invalid file type
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "not allowed" in response.json()["detail"]

def test_upload_multiple_images(client, sample_image):
    # Test uploading multiple images to ensure unique filenames
    paths = []
    
    # Upload the same image twice
    for _ in range(2):
        with open(sample_image, "rb") as f:
            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
        
        assert response.status_code == 200
        paths.append(response.json()["file_path"])
    
    # Verify paths are different
    assert len(paths) == 2
    assert paths[0] != paths[1]
    assert all(os.path.exists(path) for path in paths)

def test_upload_large_image(client, tmp_path):
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

def test_concurrent_uploads(client, sample_image):
    # Test uploading multiple files concurrently
    paths = []
    
    # Upload multiple files sequentially (since TestClient is synchronous)
    for _ in range(5):
        with open(sample_image, "rb") as f:
            response = client.post(
                "/upload/",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
            assert response.status_code == 200
            paths.append(response.json()["file_path"])
    
    # Verify all uploads were successful and unique
    assert len(paths) == 5
    assert len(set(paths)) == 5  # All paths should be unique
    assert all(os.path.exists(path) for path in paths)

def test_process_image_with_caption(client, realistic_image):
    """
    End-to-end test of image processing with real caption generation.
    Tests both the file upload and caption generation with the actual BLIP model.
    """
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": ("scene.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify file handling
    assert "file_path" in data
    assert os.path.exists(data["file_path"])
    
    # Verify caption generation
    assert "caption" in data
    assert isinstance(data["caption"], str)
    assert len(data["caption"]) > 0
    
    # Verify caption content (should contain relevant keywords for our test image)
    caption = data["caption"].lower()
    assert any(word in caption for word in ["blue", "sky", "green", "landscape", "scene", "view"])

def test_process_invalid_image(client, tmp_path):
    # Create an invalid file
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("This is not an image")
    
    # Test processing an invalid file
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "not allowed" in response.json()["detail"]

def test_process_corrupted_image(client, tmp_path):
    # Create a corrupted image file
    corrupted_image = tmp_path / "corrupted.jpg"
    with open(corrupted_image, "wb") as f:
        f.write(b"This is not a valid JPG file but has .jpg extension")
    
    # Test processing a corrupted image
    with open(corrupted_image, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": ("corrupted.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to process image" in response.json()["detail"] 