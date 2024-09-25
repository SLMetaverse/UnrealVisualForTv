import argparse
import os
import unreal
import shutil


from SequenceHandler import SequenceHandler
from APIHandler import APIHandler
from EnvManager import EnvManager
import os
from scripts.a2f import convert_audio_to_facial
from scripts.usd2facial import convert_usd_to_animation



working_directory = unreal.Paths.project_dir()
# Create the folder relative to the working directory
download_folder = os.path.join(working_directory, "Saved", "TempFiles")


class Initialize:
    def __init__(self):
        if os.path.exists(download_folder):
            shutil.rmtree(download_folder)  # Use rmtree to remove the directory and its contents
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--shotId", required=True)
        parser.add_argument("-r", "--renderQuality", required=True)
        parser.add_argument("-p", "--isprod", required=True, default=False, type=lambda x: (str(x).lower() == 'true'))
        
        args = parser.parse_args()
        
        self.shotId = args.shotId
        self.renderQuality = None or args.renderQuality
        self.IsProd = args.isprod
        
        print(70*"-")
        print(f"IsProduction: {self.IsProd}")
        print(f"renderQuality: {self.renderQuality}")
        print(f"ID: {self.shotId}")
        print(70*"-")
        
        os.environ['ISPROD'] = "True" if self.IsProd else "False"
        
    def process_json_data(self, data):
        """
        Processes the JSON data to extract necessary information.
        
        :param data: The JSON data to process.
        :return: Processed information or actions based on the JSON data.
        """
        title = data.get('title', '')
        script = data.get('script', '')
        transition_in = data.get('transitionIn', 'None')
        transition_out = data.get('transitionOut', 'None')
        shot_type = data.get('shotType', '')
        shot_cast = data.get('shotCast', [])
        audio_url = data.get('audioUrl', '')
        audio_duration = data.get('audioDuration', 0.0)

        # Extract place information
        place = data.get('place', {})

        # You can add further logic here to pass this data to your Unreal Engine scripts,
        # create sequences, etc.
        # Pass data to handler functions
        handler = SequenceHandler(audio_duration)
        handler.setup_camera_location()
        handler.setup_place_background(place_data=place)

        audio_file_name = handler.handle_audio(audio_url=audio_url)
        out_usd_file = convert_audio_to_facial(audio_file_name + ".wav")

        anim_path = convert_usd_to_animation(out_usd_file)
        # anim_path = convert_usd_to_animation("C:/Users/anup/Developer/VisualForTV/Saved/TempFiles/usd_animations/audio.usd")


        handler.handle_camera_shot(shot_type)
        handler.handle_metahuman("Aoi", "middle", 0, anim_path)

        handler.renderVideo(self.shotId, self.renderQuality)

    def get_shot_id_from_args(self):
        return self.shotId


if __name__ == '__main__':
    initialize = Initialize()
    shot_id= initialize.get_shot_id_from_args()

    #env_manager = EnvManager()
    print(f"EnvINSTANCE  = {EnvManager()._instance}")
    print(f"EnvINSTANCE BASE URL  = {EnvManager()._instance.get_base_url()}")

    api_handler = APIHandler(base_url=EnvManager()._instance.get_base_url())
    
      # Attempt to log in
    if api_handler.login():
        print("Login successful!")
        
        # Now retrieve the JSON data
        json_data = api_handler.get(endpoint=f"storyboard/shots/video-generation/{shot_id}")
        if json_data:
            print(json_data)
            initialize.process_json_data(json_data)
    else:
        print("Login failed.")
        # Exit Unreal if login fails
        unreal.SystemLibrary.quit_editor()
    
