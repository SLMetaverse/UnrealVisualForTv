import py_audio2face as pya2f
import os
import logging

# from scripts.usd2facial import convert_usd_to_animation

# Set up logging configuration
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

def convert_audio_to_facial(working_dir, audio_file_name):
    # Define the audio input path

    base_dir = os.path.join(working_dir, "audio")


    audio_file_path = os.path.join(base_dir, audio_file_name)

    # Create the output file name based on the audio file name
    output_file_name = os.path.splitext(audio_file_name)[0] + ".usd"  # Change extension to .usd
    output_file_path: str | bytes = os.path.join(working_dir, "animations", output_file_name)

    logger.debug(f'Starting conversion for {audio_file_path}.')

    # Initialize Audio2Face
    a2f = pya2f.Audio2Face()
    try:
        a2f.init_a2f()
        logger.debug('Audio2Face initialized successfully.')

        # Call audio2face_single with the specified paths
        result = a2f.audio2face_single(
            audio_file_path=audio_file_path,
            output_path=output_file_path,
            fps=60,
            emotion_auto_detect=True
        )

        # If the result contains the new file name, rename the output file
        if result:
            logger.debug(f'Output stored to: {result}')
            new_output_file_path = os.path.join(base_dir, "animations", result)  # Assuming result gives the filename
            os.rename(output_file_path + "_bsweight.usd", new_output_file_path)  # Rename the file
            logger.debug(f'Output file renamed to: {new_output_file_path}')
            return new_output_file_path
        else:
            logging.warning('No output file returned from audio2face_single.')

    except Exception as e:
        logging.error(f'Error during conversion: {e}')
        return None