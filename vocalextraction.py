import os
import subprocess
from pydub import AudioSegment

class VocalExtractor:
    def __init__(self, model_name="htdemucs", output_dir="demucs_output"):
        self.model_name = model_name
        self.output_dir = output_dir

    def extract_vocals(self, audio_path):
        os.makedirs(self.output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        vocal_path = os.path.join(self.output_dir, self.model_name, base_name, "vocals.wav")

        if os.path.exists(vocal_path):
            return AudioSegment.from_wav(vocal_path)

        subprocess.run(["demucs", "-n", self.model_name, "-o", self.output_dir, audio_path])

        return AudioSegment.from_wav(vocal_path)
    
    def remove_extracted_vocals(self, audio_path):
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_dir = os.path.join(self.output_dir, self.model_name, base_name)

        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
            os.rmdir(output_dir)
            print(f"Removed output directory: {output_dir}")
        else:
            print(f"No extracted files found for {audio_path}")