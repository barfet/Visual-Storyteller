from fastapi import FastAPI, UploadFile, File, HTTPException
from src.services.file_service import FileService, InvalidFileTypeError

app = FastAPI(title="Visual Storyteller")
file_service = FileService()

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