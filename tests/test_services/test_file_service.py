import os
import pytest
import aiofiles
import tempfile
from fastapi import UploadFile
from pathlib import Path
from src.services.file_service import FileService, InvalidFileTypeError

@pytest.fixture
def file_service():
    # Create a temporary test directory
    test_upload_dir = "test_uploads"
    os.makedirs(test_upload_dir, exist_ok=True)
    
    service = FileService(upload_dir=test_upload_dir)
    yield service
    
    # Cleanup after tests
    for file in Path(test_upload_dir).glob("*"):
        file.unlink()
    os.rmdir(test_upload_dir)

@pytest.fixture
def sample_image(tmp_path):
    # Create a sample image file for testing
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"fake image content")
    return image_path

@pytest.mark.asyncio
async def test_valid_file_upload(file_service, sample_image):
    # Create a temporary file for UploadFile
    temp_file = tempfile.SpooledTemporaryFile()
    temp_file.write(b"fake image content")
    temp_file.seek(0)
    
    # Create UploadFile instance
    upload_file = UploadFile(filename="test.jpg", file=temp_file)
    file_path = await file_service.save_upload(upload_file)
    
    assert os.path.exists(file_path)
    assert file_path.endswith(".jpg")
    
    # Cleanup
    temp_file.close()

@pytest.mark.asyncio
async def test_invalid_file_type(file_service, tmp_path):
    # Create a temporary file for UploadFile
    temp_file = tempfile.SpooledTemporaryFile()
    temp_file.write(b"some text")
    temp_file.seek(0)
    
    # Create UploadFile instance
    upload_file = UploadFile(filename="test.txt", file=temp_file)
    
    with pytest.raises(InvalidFileTypeError):
        await file_service.save_upload(upload_file)
    
    # Cleanup
    temp_file.close()

@pytest.mark.asyncio
async def test_unique_filename_generation(file_service, sample_image):
    # Create temporary files for UploadFile
    temp_file1 = tempfile.SpooledTemporaryFile()
    temp_file1.write(b"fake image content")
    temp_file1.seek(0)
    
    temp_file2 = tempfile.SpooledTemporaryFile()
    temp_file2.write(b"fake image content")
    temp_file2.seek(0)
    
    # Create UploadFile instances
    upload_file1 = UploadFile(filename="test.jpg", file=temp_file1)
    upload_file2 = UploadFile(filename="test.jpg", file=temp_file2)
    
    path1 = await file_service.save_upload(upload_file1)
    path2 = await file_service.save_upload(upload_file2)
    
    assert path1 != path2
    
    # Cleanup
    temp_file1.close()
    temp_file2.close() 