import os
import pytest
from pathlib import Path
from PIL import Image
from unittest.mock import Mock, patch, ANY
import torch
from src.services.captioning_service import CaptioningService

@pytest.fixture
def mock_processor():
    processor = Mock()
    # Mock the processor's behavior
    processor.return_value = {"pixel_values": torch.zeros((1, 3, 224, 224))}
    processor.decode.return_value = "a test caption"
    return processor

@pytest.fixture
def mock_model():
    model = Mock()
    # Mock the model's behavior
    model.generate.return_value = [torch.tensor([1, 2, 3])]
    model.to.return_value = model  # For device movement
    return model

@pytest.fixture
def captioning_service(mock_processor, mock_model):
    return CaptioningService(processor=mock_processor, model=mock_model)

@pytest.fixture
def sample_image(tmp_path):
    # Create a sample image for testing
    image_path = tmp_path / "test.jpg"
    image = Image.new('RGB', (100, 100), color='red')
    image.save(image_path)
    return image_path

@pytest.mark.asyncio
async def test_generate_caption(captioning_service, sample_image, mock_processor, mock_model):
    # Test that a caption is generated for a valid image
    caption = await captioning_service.generate_caption(str(sample_image))
    
    # Verify the caption is returned
    assert isinstance(caption, str)
    assert caption == "a test caption"
    
    # Verify our mocks were called correctly
    mock_processor.assert_called_once()
    mock_model.generate.assert_called_once()
    # Use ANY for tensor comparison since we can't directly compare tensors
    mock_processor.decode.assert_called_once_with(ANY, skip_special_tokens=True)

@pytest.mark.asyncio
async def test_invalid_image_path(captioning_service):
    # Test that an error is raised for non-existent image
    with pytest.raises(FileNotFoundError):
        await captioning_service.generate_caption("nonexistent.jpg")

@pytest.mark.asyncio
async def test_invalid_image_format(captioning_service, tmp_path):
    # Create an invalid image file
    invalid_image = tmp_path / "invalid.jpg"
    with open(invalid_image, "w") as f:
        f.write("This is not an image")
    
    # Test that an error is raised for invalid image format
    with pytest.raises(Exception):
        await captioning_service.generate_caption(str(invalid_image)) 