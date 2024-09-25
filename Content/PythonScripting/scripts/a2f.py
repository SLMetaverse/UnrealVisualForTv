import os
import unreal
import requests

from APIHandler import APIHandler

working_directory = unreal.Paths.project_dir()

# Create the folder relative to the working directory
base_dir = os.path.join(working_directory, "Saved", "TempFiles")
base_unreal_assets_dir = os.path.join(base_dir, "Audio")

url =  "http://bear-primary-clearly.ngrok-free.app/"

def convert_audio_to_facial(audio_file_name):
    # Define the audio input path
    audio_file_path = os.path.join(base_unreal_assets_dir, audio_file_name)

    with open(audio_file_path, 'rb') as audio_file:
        files = {'file': audio_file}
        response = requests.post(f'{url}/upload-audio', files=files, verify=False)

    filename = response.json().get('filename')

    api_handler = APIHandler(
        base_url=f'{url}/get-file/{filename}')

    download_success = api_handler.download_file(
        "usd_animations",  # This is the folder name where the image is to be saved inside unreal engine
        f'{filename}',
        False
    )

    if download_success:
        rel_path = os.path.join(base_dir, "usd_animations", filename)
        return os.path.abspath(rel_path)  # Return the absolute disk path

