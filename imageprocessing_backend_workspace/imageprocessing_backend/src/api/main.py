import os
import shutil
from uuid import uuid4
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from pydantic import BaseModel, Field
from PIL import Image, ImageFilter

# PUBLIC_INTERFACE
def get_image_dir():
    """Returns the path to the directory where images are stored."""
    img_dir = os.path.join(os.path.dirname(__file__), "..", "images")
    abs_img_dir = os.path.abspath(img_dir)
    os.makedirs(abs_img_dir, exist_ok=True)
    return abs_img_dir

app = FastAPI(
    title="Image Processing API",
    description="REST API for uploading, processing, and retrieving images.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Image Upload", "description": "Upload new images for processing."},
        {"name": "Image Processing", "description": "Process images (resize, filter, convert format)."},
        {"name": "Image Retrieval", "description": "Retrieve original or processed images."},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_FORMATS = ["jpeg", "png", "webp"]
SUPPORTED_FILTERS = ["BLUR", "CONTOUR", "DETAIL", "EDGE_ENHANCE", "SHARPEN", "SMOOTH"]


class ImageListResponse(BaseModel):
    filenames: List[str] = Field(..., description="List of available image files (original and processed)")


class ProcessImageRequest(BaseModel):
    width: Optional[int] = Field(None, description="Target width for resizing")
    height: Optional[int] = Field(None, description="Target height for resizing")
    format: Optional[str] = Field(None, description="Target image format (jpeg, png, webp)")
    filter: Optional[str] = Field(None, description=f"Image filter to apply: {', '.join(SUPPORTED_FILTERS)}")


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health check", operation_id="health_check")
def health_check():
    """Health check endpoint
    Returns simple health check message.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.post("/upload", status_code=status.HTTP_201_CREATED, tags=["Image Upload"], summary="Upload an image", operation_id="upload_image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a new image to the server.
    - **file**: Image file (JPEG, PNG, WEBP)
    Returns a unique filename for later processing or retrieval.
    """
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported image format: {ext}")
    unique_id = uuid4().hex
    save_name = f"{unique_id}.{ext}"
    dest_dir = get_image_dir()
    dest_path = os.path.join(dest_dir, save_name)

    with open(dest_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {"filename": save_name}


# PUBLIC_INTERFACE
@app.get("/images", response_model=ImageListResponse, tags=["Image Retrieval"], summary="List available images", operation_id="list_images")
def list_images() -> ImageListResponse:
    """
    Returns a list of uploaded and processed image files, available by their filename.
    """
    dir_path = get_image_dir()
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    return ImageListResponse(filenames=files)


# PUBLIC_INTERFACE
@app.get("/image/{filename}", tags=["Image Retrieval"], summary="Get an image", operation_id="get_image")
def get_image(filename: str):
    """
    Retrieve an image by filename.
    - **filename**: Image filename (from /images)
    Returns the image file for download or preview.
    """
    img_dir = get_image_dir()
    file_path = os.path.join(img_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    # Return image as file response with correct content type
    ext = filename.split(".")[-1].lower()
    content_type = f"image/{'jpeg' if ext == 'jpg' else ext}"
    return FileResponse(file_path, media_type=content_type, filename=filename)


# PUBLIC_INTERFACE
@app.post("/process/{filename}", tags=["Image Processing"], summary="Process an image", operation_id="process_image")
def process_image(
    filename: str,
    width: Optional[int] = Query(None, description="Resize width"),
    height: Optional[int] = Query(None, description="Resize height"),
    format: Optional[str] = Query(None, description="Convert format (jpeg, png, webp)"),
    filter: Optional[str] = Query(None, description=f"Image filter: {', '.join(SUPPORTED_FILTERS)}")
):
    """
    Process an existing image.
    - **filename**: Source image filename (from /images)
    - **width**: Width to resize to
    - **height**: Height to resize to
    - **format**: New format ('jpeg', 'png', 'webp')
    - **filter**: Filter to apply (BLUR, CONTOUR, etc.)
    Returns processed image; also saves processed copy with a new filename.
    """
    img_dir = get_image_dir()
    src_path = os.path.join(img_dir, filename)
    if not os.path.isfile(src_path):
        raise HTTPException(status_code=404, detail="Source file not found")

    try:
        with Image.open(src_path) as img:
            # Resize
            if width or height:
                orig_w, orig_h = img.size
                new_w = width if width else orig_w
                new_h = height if height else orig_h
                img = img.resize((new_w, new_h), Image.LANCZOS)
            # Filter
            if filter:
                pilfilter = getattr(ImageFilter, filter.upper(), None)
                if pilfilter is None or filter.upper() not in SUPPORTED_FILTERS:
                    raise HTTPException(status_code=400, detail=f"Unsupported filter: {filter}")
                img = img.filter(pilfilter)

            # Format conversion
            if format:
                out_format = format.lower()
                if out_format not in SUPPORTED_FORMATS:
                    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
            else:
                out_format = img.format.lower() if img.format else "png"

            base_name, _ = os.path.splitext(filename)
            out_filename = f"{base_name}_processed"
            if width or height:
                out_filename += f"_resized"
            if filter:
                out_filename += f"_{filter.lower()}"
            out_filename += f".{out_format}"

            out_path = os.path.join(img_dir, out_filename)
            img.save(out_path, out_format.upper())

            # Return image as response
            content_type = f"image/{'jpeg' if out_format == 'jpg' else out_format}"
            return FileResponse(out_path, media_type=content_type, filename=out_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# PUBLIC_INTERFACE
@app.delete("/image/{filename}", tags=["Image Retrieval"], summary="Delete an image", operation_id="delete_image")
def delete_image(filename: str):
    """
    Delete an image file by filename (original or processed).
    - **filename**: Image filename (from /images)
    """
    img_dir = get_image_dir()
    file_path = os.path.join(img_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"message": f"{filename} deleted"}


# PUBLIC_INTERFACE
@app.get("/docs/image-processing-help", tags=["Image Processing"], summary="API Usage Help", operation_id="api_usage_help")
def docs_image_processing_help():
    """
    Documentation endpoint describing image processing API usage, filter/format options, and sample requests.
    """
    return {
        "Supported Formats": SUPPORTED_FORMATS,
        "Supported Filters": SUPPORTED_FILTERS,
        "Example Upload": "POST /upload (multipart/form-data file)",
        "Example Resize": "POST /process/filename.png?width=200&height=100",
        "Example Filter": "POST /process/filename.png?filter=BLUR",
        "Example Convert": "POST /process/filename.png?format=jpeg"
    }
