import unreal
import utils.constants as constants

class Audio:
    def __init__(self, sequence_asset, audio_folder, audio_file_name, duration_in_seconds):
        self.sequence_asset = sequence_asset
        self.audio_path = f'/Game/Assets/{audio_folder}/{audio_file_name}'
        self.duration = duration_in_seconds

    def setup_audio_track(self):
        audio_track = self.get_audio_track()

        if(audio_track):
            # Get the first section of the audio track
            section = audio_track.get_sections()[0]
            
            # Load the audio asset
            audio_asset = unreal.EditorAssetLibrary.load_asset(self.audio_path)
            if not audio_asset:
                unreal.log_error(f"Failed to load audio asset from path: {self.audio_path}")
                return
        
            section.set_sound(audio_asset)
            section.set_range(0, self.duration * constants.FPS) # 60 is FPS of the sequencer
  
        else:
            unreal.log_error("No Audio Track Ref")

        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    def get_audio_track(self):
        """
        Retrieve the audio track from the given sequence asset.

        :param sequence_asset: The sequence asset from which to retrieve the audio track.
        :return: The audio track if found, None otherwise.
        """
        tracks = unreal.MovieSceneSequence.get_tracks(self.sequence_asset)
        for track in tracks:
            if isinstance(track, unreal.MovieSceneAudioTrack):
                return track
            
        return None