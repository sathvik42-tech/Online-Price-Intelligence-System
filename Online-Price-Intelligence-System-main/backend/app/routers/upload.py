from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "temp_uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and WebP are allowed.")

    # Validate file size (reading into memory - for larger files, consider spooled temp file checks)
    # Since we need to save it anyway, we can read and check size.
    # Alternatively, check file.size after reading if it's available.
    
    # Read file content to check size
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_id = str(uuid.uuid4())
    unique_filename = f"{unique_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    return {
        "status": "success",
        "message": "Image uploaded successfully",
        "image_id": unique_id,
        "filename": unique_filename,
        "original_filename": file.filename
    }
