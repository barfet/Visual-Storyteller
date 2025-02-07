from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from src.services.file_service import FileService, InvalidFileTypeError
from src.services.captioning_service import CaptioningService
from src.services.narrative_service import NarrativeService, NarrativeGenerationError
from src.config import settings
from typing import Optional

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
async def process_image_with_narrative(
    file: UploadFile = File(...),
    prompt_template: Optional[str] = Form(None),
    max_tokens: Optional[int] = Form(None),
    temperature: Optional[float] = Form(None)
):
    """
    Process an image file to generate both a caption and a narrative.
    
    Args:
        file: The image file to process
        prompt_template: Optional custom prompt template for narrative generation
        max_tokens: Optional maximum tokens for narrative generation
        temperature: Optional temperature for controlling narrative creativity
    
    Returns:
        dict: Contains the file path, caption, and generated narrative
    """
    try:
        # First save the file
        file_path = await file_service.save_upload(file)
        
        # Generate caption
        caption = await captioning_service.generate_caption(file_path)
        
        # Generate narrative with optional parameters
        narrative_kwargs = {}
        if prompt_template is not None:
            narrative_kwargs["prompt_template"] = prompt_template
        if max_tokens is not None:
            narrative_kwargs["max_tokens"] = int(max_tokens)  # Convert from string to int
        if temperature is not None:
            narrative_kwargs["temperature"] = float(temperature)  # Convert from string to float
            
        narrative = await narrative_service.generate_narrative(caption, **narrative_kwargs)
        
        return {
            "file_path": file_path,
            "caption": caption,
            "narrative": narrative
        }
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except NarrativeGenerationError as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": f"Invalid parameter value: {str(e)}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Failed to process image: {str(e)}"}) 