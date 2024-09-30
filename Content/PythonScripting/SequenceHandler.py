import unreal
import time
import utils.constants as constants

from scripts.background import create_background
from scripts.metahuman import MetaHuman
from scripts.Audio import Audio
from APIHandler import APIHandler
from EnvManager import EnvManager
import os



def get_camera_from_world(camera_name=None):
    """
    Retrieves a Cine Camera Actor from the world.
    :param camera_name: Optional name of the camera to search for. If None, returns the first found camera.
    :return: The Cine Camera Actor if found, otherwise None.
    """
    # Get all actors in the level
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()

    # Iterate through all actors and filter for CineCameraActor
    cameras = [actor for actor in all_actors if isinstance(actor, unreal.CineCameraActor)]

    if camera_name:
        # Filter cameras by name if a name is provided
        for camera in cameras:
            if camera.get_name() == camera_name:
                return camera
    else:
        # Return the first camera found
        if cameras:
            return cameras[0]

    # Return None if no camera is found
    return None

def create_level_sequence(duration):
    """
    Creates a new Level Sequence in the world using AssetTools.

    :return: The created Level Sequence.
    """
    # Create Sequencer
    # asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    #
    # # Define the folder and asset name
    # sequence_name = "LS_StudioMain"
    # package_path = "/Game/Sequences"
    #
    # # Create the Level Sequence
    # sequence_asset = asset_tools.create_asset(
    #     asset_name=sequence_name,
    #     package_path=package_path,
    #     asset_class=unreal.LevelSequence,
    #     factory=unreal.LevelSequenceFactoryNew()
    # )
    #
    # # Save the asset to disk
    # unreal.EditorAssetLibrary.save_loaded_asset(sequence_asset)

    default_sequencer_path = "/Game/Sequences/LS_StudioDefault"
    sequence_asset = unreal.EditorAssetLibrary.load_asset(default_sequencer_path)

    sequencer = unreal.LevelSequence.cast(sequence_asset)
    
    sequencer.set_playback_end_seconds(duration)
    
    unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    return sequencer

class SequenceHandler:
    sequencer_instance = None
    plane_actor = None
    sequence_duration = 0.0

    def __init__(self, duration):
        self.sequence_duration = duration
        self.sequencer_instance = create_level_sequence(duration)
        self.subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        self.queue = self.subsystem.get_queue()
        self.executor = unreal.MoviePipelinePIEExecutor()

    def setup_place_background(self, place_data):
        place_name = place_data.get('name', '')
        place_image_data = place_data.get('placeImage', {})
        place_image_filename = place_image_data.get('filename', '')
        place_image_mimetype = place_image_data.get('mimetype', '')
        place_file_location = place_image_data.get('location', '')

        #env_manager = EnvManager()
        print(f"EnvINSTANCE  = {EnvManager()._instance}")
        print(f"EnvINSTANCE BASE WITH CDN ENV  = {EnvManager()._instance.get_cdn_url_with_env()}")

        api_handler = APIHandler(base_url=f"{EnvManager()._instance.get_cdn_url_with_env()}/{place_file_location}/{place_image_filename}")
        
        download_success= api_handler.download_file( 
            "Backgrounds",          #This is the folder name where the image is to be saved inside unreal engine
            f"{place_image_filename}"
            )
        
        if(download_success):
            unreal.log("Success Fully Loaded File")
            base_file_name = os.path.splitext(place_image_filename)[0]
            material_path = f'/Game/Assets/Backgrounds/DefaultBg'
            plane_name = 'Background'
            new_material_name = 'BackgroundMaterial'
            aspect_ratio = 16 / 9  # Aspect ratio for the background plane
            position = unreal.Vector(0, 0, 0)  # Position of the plane in Unreal units
            scale_factor = 4.0  # Scale factor to resize the plane

            # Create Background
            self.plane_actor = create_background(plane_name, material_path, new_material_name, base_file_name, aspect_ratio, position, scale_factor)
        else:
            unreal.log_error("Failed to download Image")

    def handle_camera_shot(self, shot_type):
        """
        Handles the shot type by setting up a level sequencer, spawning a cine camera,
        and binding the camera to the sequence.

        :param shot_type: The type of shot (e.g., Close-Up, Long Shot).
        :param characters: The list of characters to focus on.
        """
        # Create a Level Sequencer and Cine Camera
        camera_actor = self.spawn_cine_camera()
        self.bind_camera_to_sequence(camera_actor)

    def spawn_cine_camera(self):
        """
        Spawns a Cine Camera Actor in the world.

        :return: The spawned Cine Camera Actor.
        """
        camera_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(0, 0, 0))

        # todo: make it dynamic
        ca = unreal.CineCameraActor.cast(camera_actor)
        camera_actor.set_actor_location(unreal.Vector(0, 460, 0), False, True)
        camera_actor.set_actor_rotation(unreal.Rotator(0, 0, -90), True)

        cp = ca.get_cine_camera_component()
        cp.set_editor_property('current_focal_length', 24)

        return camera_actor

    def bind_camera_to_sequence(self, camera_actor):
        """
        Binds a Cine Camera Actor to the Level Sequence.
        :param camera_actor: The Cine Camera Actor to bind.
        """
        sequence_binding = self.sequencer_instance.add_possessable(camera_actor)
        return sequence_binding


    def setup_camera_location(self):
        camera_actor = get_camera_from_world()
        camera_actor.set_actor_location(unreal.Vector(0, 360, 0), False, True)
        camera_actor.set_actor_rotation(unreal.Rotator(0, 0, -90), True)

    def spawn_metahuman(self, name, position, rotation):
        """
          Spawns a metahuman in the world

          :param name: The name of the character.
          :param position: The position of the character.
          :param rotation: The rotation of the character.
        """
        metahuman = MetaHuman(name, position, rotation)
        actor = metahuman.add_to_scene(self.plane_actor)

        return actor

    def bind_metahuman_to_sequence(self, metahuman_actor):
        """
        :param metahuman_actor: The Metahuman character to bind
        :return: sequence binding
        """
        sequencer = unreal.LevelSequence.cast(self.sequencer_instance)
        binding = sequencer.add_possessable(metahuman_actor)

        return binding

    def handle_metahuman(self, name, position, rotation, anim_path):
        """
          Spawns a metahuman in the world and binds the metahuman to the sequencer.

          :param anim_path: Animation to run for the metahuman
          :param name: The name of the character.
          :param position: The position of the character.
          :param rotation: The rotation of the character.
        """
        mh = self.spawn_metahuman(name, position, rotation)
        mh_parent_binding = self.bind_metahuman_to_sequence(mh)
        face_component = None

        components = mh.get_components_by_class(unreal.SkeletalMeshComponent)
        for c in components:
           if c.get_name() == "Face":
                face_component = c
                break

        face_binding = self.sequencer_instance.add_possessable(face_component)
        face_binding.set_parent(mh_parent_binding)
        anim_track = face_binding.add_track(unreal.MovieSceneSkeletalAnimationTrack)
        anim_section = anim_track.add_section()
        face_animation = unreal.EditorAssetLibrary.load_asset(anim_path)

        anim_section.set_editor_property("params", unreal.MovieSceneSkeletalAnimationParams(animation=face_animation))
        anim_section.set_range(0, self.sequence_duration * int(constants.FPS))

        return mh_parent_binding
    
    def handle_audio(self, audio_url):

        env_manager = EnvManager()
        print(f"EnvINSTANCE  = {EnvManager()._instance}")
        print(f"EnvINSTANCE BASE CDN URL  = {EnvManager()._instance.get_cdn_base_url()}")

        # This is audio_url format: "staging/storyboard-shots/53faa6c4-ca63-4dfa-a523-a6d3066d3bdc/audio.mp3"
        api_handler = APIHandler(base_url=f"{EnvManager()._instance.get_cdn_base_url()}/{audio_url}")

        audio_folder_name= "Audio"
        audio_file_name = "audio.mp3"
        asset_audio_file_name = "audio"
        
        download_success = api_handler.download_file( 
            audio_folder_name, #This is the folder name where the image is to be saved inside unreal engine
            audio_file_name,
            )

        if(download_success):
            audio= Audio(self.sequencer_instance, 
                         audio_folder_name, 
                         asset_audio_file_name,
                         self.sequence_duration)
            audio.setup_audio_track()

            unreal.log("Audio file Successfully Loaded")

            return asset_audio_file_name

        else:
            unreal.log_error("Failed to download Audio file")

    def renderVideo(self, shotId, renderQuality = "2160p60"):
        if renderQuality == "fast60":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p60audioImageFast"
        elif renderQuality == "fast24":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p24audioImageFast"
        elif renderQuality == "720p60":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p60audio"
        elif renderQuality == "1080p60":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_1080p60audio"
        elif renderQuality == "2160p60":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_2160p60audio"
        elif renderQuality == "720p24":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p24audio"
        elif renderQuality == "1080p24":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_1080p24audio"
        elif renderQuality == "2160p24":
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_2160p24audio"
        else:
            u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p24audioImageFast"


        unreal.log_warning(f"Quality: {renderQuality}, Render starts in 30 seconds...")
        time.sleep(30)
        
        u_level_file = "/Game/Maps/StudioMap"
        # u_preset_file = "/Game/Maps/LevelSequences/MConfig_720p60audioImageFast"
        job = self.queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = shotId
        job.map = unreal.SoftObjectPath(u_level_file)
        job.sequence = unreal.SoftObjectPath("/Game/Sequences/LS_StudioDefault")
        preset = unreal.EditorAssetLibrary.find_asset_data(u_preset_file).get_asset()
        job.set_configuration(preset)

        self.executor.on_executor_errored_delegate.add_callable(self.render_errored)
        self.executor.on_executor_finished_delegate.add_callable(self.render_finished)

        self.subsystem.render_queue_with_executor_instance(self.executor)

    def render_errored(self, executor, pipeline, is_fatal, error_msg):
        unreal.log_warning(
            "Render Error: \n"
            "Executor: {}\n"
            "Pipeline: {} \n"
            "Fatal? {} \n"
            "{}".format(executor, pipeline, is_fatal, error_msg)
        )

    def render_finished(self, executor, is_success):
        unreal.log_warning(
            'Render Success? {} \n'
            'Executor: {}'.format(is_success, executor)
        )
        if(is_success):
            unreal.log_warning("renderind finished... exiting in 120 sec.")
            time.sleep(120)
            unreal.log_warning("render_END")
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")