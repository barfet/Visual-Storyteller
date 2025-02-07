import os
import shutil
import pytest
from PIL import Image
import numpy as np
from src.config import settings

@pytest.fixture
def realistic_image(tmp_path):
    """Create a realistic test image with natural-looking content."""
    # Create a 640x480 RGB image with a blue sky gradient and green landscape
    width, height = 640, 480
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create sky gradient (blue)
    for y in range(height // 2):
        blue_value = int(200 + (y * 55 / (height // 2)))  # Gradient from light to darker blue
        image[y, :] = [135, 206, blue_value]
    
    # Create landscape (green)
    for y in range(height // 2, height):
        green_value = int(100 + ((y - height // 2) * 55 / (height // 2)))  # Gradient green
        image[y, :] = [34, green_value, 34]
    
    # Convert numpy array to PIL Image
    img = Image.fromarray(image)
    
    # Save the image
    test_image_path = tmp_path / "test_scene.jpg"
    img.save(test_image_path, "JPEG")
    
    return str(test_image_path)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up uploaded files after each test."""
    yield
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
        os.makedirs(settings.UPLOAD_DIR) 