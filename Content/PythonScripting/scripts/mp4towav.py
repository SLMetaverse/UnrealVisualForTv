from pydub import AudioSegment


def mp3_to_wav(input_file, output_file):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(input_file)

    # Export as WAV
    audio.export(output_file, format="wav")

    return output_file


# Usage example
# mp3_to_wav('./audio.mp3', 'output.wav')
