import os
import time
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from tests.test_api.fixtures import realistic_image, cleanup

@pytest.fixture
def client():
    return TestClient(app)

def test_process_with_tts(client, realistic_image):
    """Test complete flow from image upload to TTS generation."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "true"}
        )
    
    print("\nError response:", response.json())  # Debug print
    assert response.status_code == 200
    data = response.json()
    
    # Verify all components are present
    assert "file_path" in data
    assert "caption" in data
    assert "narrative" in data
    assert "audio_file" in data
    
    # Verify files exist
    assert os.path.exists(data["file_path"])
    assert os.path.exists(data["audio_file"])
    assert data["audio_file"].endswith(".mp3")

def test_tts_with_custom_language(client, realistic_image):
    """Test TTS generation with custom language."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "true", "language": "fr"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "audio_file" in data
    assert os.path.exists(data["audio_file"])

def test_tts_disabled(client, realistic_image):
    """Test that TTS is not generated when disabled."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "false"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "audio_file" not in data

def test_audio_file_retrieval(client, realistic_image):
    """Test retrieving generated audio file."""
    # First generate the audio file
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "true"}
        )
    
    data = response.json()
    audio_filename = os.path.basename(data["audio_file"])
    
    # Then try to retrieve it
    response = client.get(f"/audio/{audio_filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"

def test_invalid_audio_file_retrieval(client):
    """Test retrieving non-existent audio file."""
    response = client.get("/audio/nonexistent.mp3")
    assert response.status_code == 404

def test_tts_performance(client, realistic_image):
    """Test TTS generation performance."""
    start_time = time.time()
    
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "true"}
        )
    
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    assert processing_time <= 20  # Allow up to 20 seconds for the complete pipeline
    assert "audio_file" in response.json()

def test_tts_error_handling(client, realistic_image):
    """Test error handling with invalid language."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"tts": "true", "language": "invalid_lang"}
        )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"] 