import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import logging
import shutil

from convert import convert_audio_to_facial  # Ensure this function is defined in convert.py

app = FastAPI()

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the directory in the project to store uploaded audio files
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
ANIMATIONS_DIR = os.path.join(UPLOAD_DIR, "animations")

def create_dir():
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    # Create the upload directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ANIMATIONS_DIR, exist_ok=True)

@app.get("/")
async def root():
    logger.debug("Hello world")
    return {"message": "Hello World"}

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    logger.debug('Creating Directories')
    create_dir()

    logger.debug(f'Created {AUDIO_DIR} and {ANIMATIONS_DIR}')

    # Create a secure filename to prevent directory traversal attacks
    file_location = os.path.join(AUDIO_DIR, file.filename)

    # Read the content of the file and save it
    with open(file_location, "wb") as audio_file:
        content = await file.read()
        audio_file.write(content)

    # Get content_type from the UploadFile object
    content_type = file.content_type or "audio/wav"  # Default to WAV if None

    output_file_path = convert_audio_to_facial(UPLOAD_DIR, file.filename)  # Ensure this function returns the correct output path

    if output_file_path and os.path.exists(output_file_path):
        return {"filename": os.path.basename(output_file_path)}

    return {"error": "File conversion failed or output file not found."}

@app.get("/get-file/{filename}")
async def get_file(filename: str):
    # Construct the path to the file in the animations directory
    file_path = os.path.join(ANIMATIONS_DIR, filename)

    # Check if the file exists
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='model/vnd.pixar.usd', filename=filename)

    return {"error": "File not found."}
