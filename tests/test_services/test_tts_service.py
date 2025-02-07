import os
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch
from src.services.tts_service import TTSService, TTSError

@pytest.fixture
def tts_service(tmp_path):
    """Create a TTS service instance with a temporary output directory."""
    return TTSService(output_dir=str(tmp_path))

@pytest.fixture
def mock_gtts():
    """Mock gTTS instance."""
    with patch('src.services.tts_service.gTTS') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_text_to_speech(tts_service, mock_gtts):
    """Test successful text-to-speech conversion."""
    text = "This is a test narrative."
    
    # Generate audio
    file_path = await tts_service.text_to_speech(text)
    
    # Verify gTTS was called correctly
    mock_gtts.save.assert_called_once()
    assert file_path.endswith(".mp3")
    assert os.path.dirname(file_path) == tts_service.output_dir

@pytest.mark.asyncio
async def test_empty_text(tts_service):
    """Test that empty text raises an error."""
    with pytest.raises(ValueError) as exc_info:
        await tts_service.text_to_speech("")
    
    assert "Text cannot be empty" in str(exc_info.value)

@pytest.mark.asyncio
async def test_custom_filename(tts_service, mock_gtts):
    """Test text-to-speech with custom filename."""
    text = "This is a test narrative."
    filename = "custom_audio.mp3"
    
    file_path = await tts_service.text_to_speech(text, filename=filename)
    
    assert os.path.basename(file_path) == filename
    mock_gtts.save.assert_called_once()

@pytest.mark.asyncio
async def test_tts_error(tts_service, mock_gtts):
    """Test handling of TTS conversion errors."""
    mock_gtts.save.side_effect = Exception("TTS conversion failed")
    
    with pytest.raises(TTSError) as exc_info:
        await tts_service.text_to_speech("Test text")
    
    assert "Failed to convert text to speech" in str(exc_info.value)

@pytest.mark.asyncio
async def test_custom_language(tts_service, mock_gtts):
    """Test text-to-speech with custom language."""
    text = "Bonjour, c'est un test."
    language = "fr"
    
    await tts_service.text_to_speech(text, language=language)
    
    # Verify gTTS was called with correct language
    mock_gtts.save.assert_called_once()

def test_cleanup_old_files(tts_service, tmp_path):
    """Test cleanup of old audio files."""
    # Create some test files
    old_file = tmp_path / "old_audio.mp3"
    new_file = tmp_path / "new_audio.mp3"
    
    # Create files with different timestamps
    old_file.touch()
    new_file.touch()
    
    # Set old file's modification time to 25 hours ago
    old_time = time.time() - (25 * 3600)
    os.utime(old_file, (old_time, old_time))
    
    # Run cleanup
    tts_service.cleanup_old_files(max_age_hours=24)
    
    # Verify old file was deleted but new file remains
    assert not old_file.exists()
    assert new_file.exists() 