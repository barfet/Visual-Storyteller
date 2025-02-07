import os
import time
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from tests.test_api.fixtures import realistic_image

@pytest.fixture
def client():
    return TestClient(app)

def test_generate_narrative_from_image(client, realistic_image):
    """Test complete flow from image upload to narrative generation."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify file handling
    assert "file_path" in data
    assert os.path.exists(data["file_path"])
    
    # Verify caption and narrative
    assert "caption" in data
    assert "narrative" in data
    assert isinstance(data["narrative"], str)
    assert len(data["narrative"].split()) >= 20  # At least 20 words
    
    # Verify narrative coherence with caption
    caption_words = set(data["caption"].lower().split())
    narrative_words = set(data["narrative"].lower().split())
    assert len(caption_words.intersection(narrative_words)) > 0

def test_narrative_generation_with_custom_prompt(client, realistic_image):
    """Test narrative generation with custom prompt template."""
    mysterious_prompt = "Create a mysterious and intriguing story about this scene: {caption}"
    
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"prompt_template": mysterious_prompt}
        )
    
    print("\nError response:", response.json())  # Debug print
    assert response.status_code == 200
    data = response.json()
    narrative = data["narrative"].lower()
    
    # Check for mysterious elements in the narrative
    mysterious_indicators = ["mysterious", "strange", "unknown", "curious", "wonder", 
                           "secret", "enigma", "puzzle", "unexplained", "shadow"]
    assert any(word in narrative for word in mysterious_indicators)

def test_narrative_length_control(client, realistic_image):
    """Test that narrative length can be controlled."""
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"max_tokens": "50"}
        )
    
    assert response.status_code == 200
    data = response.json()
    narrative = data["narrative"]
    
    # Check narrative length constraints
    assert len(narrative.split()) <= 50
    assert len(narrative.split()) >= 10  # Ensure we still get meaningful content

def test_narrative_creativity_control(client, realistic_image):
    """Test that narrative creativity can be controlled."""
    # Generate two narratives with different temperature settings
    with open(realistic_image, "rb") as f:
        response1 = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"temperature": "0.2"}
        )
    
    with open(realistic_image, "rb") as f:
        response2 = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")},
            data={"temperature": "0.8"}
        )
    
    narrative1 = response1.json()["narrative"]
    narrative2 = response2.json()["narrative"]
    
    # Verify both narratives are meaningful
    assert len(narrative1.split()) >= 10
    assert len(narrative2.split()) >= 10
    assert "." in narrative1 and "." in narrative2  # Complete sentences
    
    # Verify narratives are different (creativity impact)
    assert narrative1 != narrative2

def test_narrative_error_handling(client, tmp_path):
    """Test error handling with corrupted image."""
    corrupted_image = tmp_path / "corrupted.jpg"
    with open(corrupted_image, "wb") as f:
        f.write(b"This is not a valid JPG file")
    
    with open(corrupted_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("corrupted.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"]

def test_narrative_performance(client, realistic_image):
    """Test narrative generation performance."""
    start_time = time.time()
    
    with open(realistic_image, "rb") as f:
        response = client.post(
            "/process_with_narrative/",
            files={"file": ("scene.jpg", f, "image/jpeg")}
        )
    
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    assert processing_time <= 15  # Allow up to 15 seconds for real API calls
    
    # Verify we got meaningful content despite performance requirements
    narrative = response.json()["narrative"]
    assert len(narrative.split()) >= 20
    assert "." in narrative  # Complete sentences 