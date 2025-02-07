import os
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from tests.test_api.fixtures import realistic_image

@pytest.fixture
def client():
    return TestClient(app)

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
    """Test processing an invalid file type."""
    # Create an invalid file
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("This is not an image")
    
    with open(invalid_file, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "not allowed" in response.json()["detail"]

def test_process_corrupted_image(client, tmp_path):
    """Test processing a corrupted image file."""
    # Create a corrupted image file
    corrupted_image = tmp_path / "corrupted.jpg"
    with open(corrupted_image, "wb") as f:
        f.write(b"This is not a valid JPG file but has .jpg extension")
    
    with open(corrupted_image, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": ("corrupted.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to process image" in response.json()["detail"] 