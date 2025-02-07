import os
import uuid
import aiofiles
from fastapi import UploadFile
from pathlib import Path

class InvalidFileTypeError(Exception):
    """Raised when an invalid file type is uploaded."""
    pass

class FileService:
    """Service for handling file uploads and storage."""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    
    def __init__(self, upload_dir: str = "data/sample_images"):
        """Initialize the file service with a upload directory."""
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract and validate file extension."""
        extension = os.path.splitext(filename)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                f"File type {extension} not allowed. Allowed types: {self.ALLOWED_EXTENSIONS}"
            )
        return extension
    
    async def save_upload(self, upload_file: UploadFile) -> str:
        """
        Save an uploaded file with a unique filename.
        
        Args:
            upload_file: The uploaded file object
            
        Returns:
            str: The path where the file was saved
            
        Raises:
            InvalidFileTypeError: If the file type is not allowed
        """
        extension = self._get_file_extension(upload_file.filename)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}{extension}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save the file
        content = await upload_file.read()
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
        
        return file_path 