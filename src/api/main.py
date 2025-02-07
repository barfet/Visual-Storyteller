from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from src.services.file_service import FileService, InvalidFileTypeError
from src.services.captioning_service import CaptioningService
from src.services.narrative_service import NarrativeService, NarrativeGenerationError
from src.config import settings
from typing import Optional
from src.services.tts_service import TTSService
import os
from fastapi.responses import FileResponse

app = FastAPI(title="Visual Storyteller")

# Initialize services with config
file_service = FileService(upload_dir=settings.UPLOAD_DIR)
captioning_service = CaptioningService()
narrative_service = NarrativeService()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image file.
    
    Returns:
        dict: Contains the path where the file was saved
    """
    try:
        file_path = await file_service.save_upload(file)
        return {"file_path": file_path}
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an image file to generate a caption.
    
    Returns:
        dict: Contains the file path and generated caption
    """
    try:
        # First save the file
        file_path = await file_service.save_upload(file)
        
        # Then generate a caption
        caption = await captioning_service.generate_caption(file_path)
        
        return {
            "file_path": file_path,
            "caption": caption
        }
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_with_narrative/")
async def process_with_narrative(
    file: UploadFile = File(...),
    prompt_template: str | None = Form(None),
    max_tokens: int | None = Form(None),
    temperature: float | None = Form(None),
    tts: bool = Form(False),
    language: str | None = Form(None)
) -> dict:
    """Process an image with captioning, narrative generation, and optional TTS."""
    try:
        # Save uploaded file
        file_path = await file_service.save_upload(file)
        
        # Generate caption
        caption = await captioning_service.generate_caption(file_path)
        
        # Generate narrative
        narrative = await narrative_service.generate_narrative(
            caption,
            prompt_template=prompt_template,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response = {
            "file_path": file_path,
            "caption": caption,
            "narrative": narrative
        }
        
        # Generate TTS if requested
        if tts:
            tts_service = TTSService()
            audio_file = await tts_service.text_to_speech(narrative, language=language)
            response["audio_file"] = audio_file
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Retrieve a generated audio file.
    
    Args:
        filename: Name of the audio file to retrieve
        
    Returns:
        FileResponse: The audio file with appropriate content type
        
    Raises:
        HTTPException: 404 if file not found, 400 if invalid filename, 500 for other errors
    """
    try:
        # Validate filename to prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid filename: directory traversal not allowed"}
            )
            
        # Ensure file has .mp3 extension
        if not filename.endswith(".mp3"):
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid file format: only MP3 files are allowed"}
            )
            
        # Construct file path
        file_path = os.path.join(settings.AUDIO_DIR, filename)
        
        # Check if path exists and is a file
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail={"error": "Audio file not found"}
            )
            
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid audio file"}
            )
            
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename
        )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Failed to retrieve audio file: {str(e)}"}
        ) 