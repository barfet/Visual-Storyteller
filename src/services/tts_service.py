import os
from typing import Optional
from gtts import gTTS
from pathlib import Path
from src.config import settings

class TTSError(Exception):
    """Raised when text-to-speech conversion fails."""
    pass

class TTSService:
    """Service for converting text to speech using gTTS."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the TTS service.
        
        Args:
            output_dir: Directory to store audio files. If not provided, uses settings
        """
        self.output_dir = output_dir or settings.AUDIO_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def text_to_speech(
        self,
        text: str,
        language: str | None = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: The text to convert to speech
            language: The language code (default: settings.TTS_LANGUAGE)
            filename: Optional filename for the audio file
            
        Returns:
            str: Path to the generated audio file
            
        Raises:
            TTSError: If text-to-speech conversion fails
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        try:
            # Use default language from settings if not provided
            lang = language or settings.TTS_LANGUAGE
            
            # Generate audio file
            tts = gTTS(text=text, lang=lang)
            
            # Create unique filename if not provided
            if not filename:
                import uuid
                filename = f"audio_{uuid.uuid4()}.mp3"
            
            # Ensure filename has .mp3 extension
            if not filename.endswith(".mp3"):
                filename += ".mp3"
            
            # Save to file
            file_path = os.path.join(self.output_dir, filename)
            tts.save(file_path)
            
            return file_path
            
        except Exception as e:
            raise TTSError(f"Failed to convert text to speech: {str(e)}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up audio files older than specified age.
        
        Args:
            max_age_hours: Maximum age of files in hours before deletion
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for file_path in Path(self.output_dir).glob("*.mp3"):
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
        except Exception as e:
            # Log error but don't raise - cleanup failures shouldn't break the service
            print(f"Warning: Failed to cleanup old audio files: {str(e)}") 