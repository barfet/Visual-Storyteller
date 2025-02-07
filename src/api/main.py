from fastapi import FastAPI, UploadFile, File, HTTPException
from src.services.file_service import FileService, InvalidFileTypeError
from src.services.captioning_service import CaptioningService

app = FastAPI(title="Visual Storyteller")
file_service = FileService()
captioning_service = CaptioningService()

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