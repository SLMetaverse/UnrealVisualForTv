import requests
import json
from requests.exceptions import HTTPError
import os
import unreal
from PIL import Image  # Import Pillow for image conversion
from EnvManager import EnvManager

from scripts.mp4towav import mp3_to_wav


class APIHandler:
    def __init__(self, base_url, headers=None):
        """
        Initializes the API handler with an optional authorization token.

        :param base_url: The base URL of the API.
        :param token: Optional token for authorization (e.g., Bearer token).
        :param headers: Optional headers for the API requests.
        """
        self.base_url = base_url
        self.headers = headers if headers else {"Content-Type": "application/json; charset=UTF-8"}

    def get(self, endpoint, params=None):
        """
        Handles GET requests.

        :param endpoint: The API endpoint for the GET request.
        :param params: Optional query parameters for the request.
        :return: The response data as JSON.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return JSON data
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def login(self):
            """
            Handles user login and updates the authorization token.

            :param username: The username for login.
            :param password: The password for login.
            :return: True if login was successful, False otherwise.
            """
            
            username = EnvManager()._instance.get_username()  # Method to get username from env
            password = EnvManager()._instance.get_password()  # Method to get password from env
            
            endpoint = "auth/login"  # Login endpoint
            data = {
                "username": username,
                "password": password
            }
            response = self.post(endpoint, data)
            if response and 'accessToken' in response:
                # Update the auth token in both headers and environment
                new_token = response['accessToken']  # Access 'accessToken'
                self.headers["Authorization"] = f"Bearer {new_token}"
                return True
            return False

    def post(self, endpoint, data):
        """
        Handles POST requests.

        :param endpoint: The API endpoint for the POST request.
        :param data: The data to send in the POST request (typically a dictionary).
        :return: The response data as JSON.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return JSON data
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def convert_webp_to_png(self, webp_file_path):
        """
        Converts a .webp file to .png.
        :param webp_file_path: Path to the .webp file.
        :return: Path to the converted .png file.
        """
        png_file_path = webp_file_path.replace(".webp", ".png")
        with Image.open(webp_file_path) as img:
            img.save(png_file_path, "PNG")
        return png_file_path

    def download_file(self, file_folder_name, file_name, import_to_unreal=True):
        """
                Download file and import it to unreal content drawer.
                :param import_to_unreal: Import to unreal or not.
                :param file_folder_name: Folder Name where it will be imported inside unreal editor.
                :param file_name: Name of the file
        """
        temp_save_path = ""
        try:
            # Get the relative path to the working directory
            working_directory = unreal.Paths.project_dir()

            # Create the folder relative to the working directory
            download_folder = os.path.join(working_directory, "Saved", "TempFiles", file_folder_name)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)        
                print(f"Make Dir :: {download_folder}")    

            # Set the save path to the folder within the working directory
            temp_save_path = os.path.join(download_folder, file_name)
            print(f"Temp Save Path :: {temp_save_path}")
            
            response = requests.get(f"{self.base_url}", stream=True, verify=False)
            response.raise_for_status()

            with open(temp_save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded to temp location: {temp_save_path}")

            # Convert the .webp file to .png
            if file_name.endswith(".webp"):
                temp_save_path = self.convert_webp_to_png(temp_save_path)
                file_name = file_name.replace(".webp", ".png")

            if file_name.endswith(".mp3"):
                output_path = temp_save_path.replace(".mp3", "")
                temp_save_path = mp3_to_wav(temp_save_path, f'{output_path}.wav')
                file_name = file_name.replace(".mp3", ".wav")

            if import_to_unreal:
                # Define the final Unreal Engine path
                unreal_folder_path = f"/Game/Assets/{file_folder_name}"
                asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

                # Use the import_asset_tasks method
                asset_import_task = unreal.AssetImportTask()
                asset_import_task.filename = temp_save_path
                asset_import_task.destination_path = unreal_folder_path
                asset_import_task.save = True
                asset_import_task.automated = True

                asset_tools.import_asset_tasks([asset_import_task])

                print(f"File imported successfully into Unreal Engine folder: {unreal_folder_path}/{file_name}")
                return True

            return True

        except requests.exceptions.HTTPError as http_err:
            unreal.log_error(f"HTTP error occurred: {http_err}")
            return False

        except Exception as err:
            unreal.log_error(f"An error occurred: {err}")
            return False
        
        # finally:
        #     # Clean up the temporary file
        #     if os.path.exists(temp_save_path):
        #         os.remove(temp_save_path)