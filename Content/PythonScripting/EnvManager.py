import os 
import unreal
from dotenv import dotenv_values

class EnvManager:
    _instance = None
    _env_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvManager, cls).__new__(cls)
            cls._load_env()
        return cls._instance

    @classmethod
    def _load_env(cls):
        is_prod = os.getenv("ISPROD", "False")  # Default to "False" if ISPROD is not set
        env_file = "prod.env" if is_prod == "True" else "test.env"
        
        # Get the project directory from Unreal
        working_directory = unreal.Paths.project_dir()

        # Construct the full path to the .env file inside the project directory
        env_file_path = os.path.join(working_directory, "Content", "PythonScripting", env_file)

        # Load environment variables if the .env file exists
        if os.path.exists(env_file_path):
            cls._env_data = dotenv_values(env_file_path)
            print(f"Loaded env data: {cls._env_data}")
        else:
            print(f"Env file not found at: {env_file_path}")
            cls._env_data = {}

    @classmethod
    def _get_env_variable(cls, key):
        """Helper function to retrieve env variables."""
        # Check if the key is present in the system's environment or the loaded .env file
        return os.getenv(key, cls._env_data.get(key, None))

    @classmethod
    def get_base_url(cls):
        return cls._get_env_variable("BASE_URL")

    @classmethod  
    def get_cdn_base_url(cls):
        return cls._get_env_variable("CDN_BASE_URL")

    @classmethod    
    def get_cdn_url_with_env(cls):
        return cls._get_env_variable("CDN_BASE_URL_WITH_ENV")
    
    @classmethod
    def get_username(cls):
        """Retrieves the username from the environment variables."""
        return cls._get_env_variable("USER_NAME")

    @classmethod
    def get_password(cls):
        """Retrieves the password from the environment variables."""
        return cls._get_env_variable("PASSWORD")

