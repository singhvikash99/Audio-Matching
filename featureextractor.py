import hashlib
import numpy as np
import librosa
from abc import ABC, abstractmethod
import base64
from python_speech_features import mfcc

# class FeatureExtractorStrategy(ABC):
#     @abstractmethod
#     def extract_feature(self, audio_file):
#         pass


class HashingHelper:
    @staticmethod
    def hash_feature(feature):
        feature_str = ",".join(map(str, feature))
        encoded = base64.b64encode(feature_str.encode()).decode()
        return encoded

    @staticmethod
    def decode(encoded_feature):
        decoded_bytes = base64.b64decode(encoded_feature)
        decoded_str = decoded_bytes.decode()
        feature = decoded_str.split(",")
        return feature


# class FeatureExtractorBase(FeatureExtractorStrategy):
#     def load_audio_segment(self, audio_file):
#         return librosa.load(audio_file, sr=None)

#     # def feature_exists(self, cursor, hashed_feature):
#     #     cursor.execute(
#     #         "SELECT COUNT(*) FROM features WHERE hashed_feature = ?",
#     #         (hashed_feature,)
#     #     )
#     #     count = cursor.fetchone()[0]
#     #     return count > 0


class MFCCExtractor:
    def extract_feature(self, audio_file):
        audio_array = np.array(audio_file.get_array_of_samples())
        return mfcc(audio_array, samplerate=audio_file.frame_rate, nfft=2048)


class TempoExtractor:
    def extract_feature(self, audio_file):
        y = np.array(audio_file.get_array_of_samples(), dtype=np.float32)
        sr = audio_file.frame_rate
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        return tempo


class ChromaExtractor:
    def extract_feature(self, audio_file):
        y = np.array(audio_file.get_array_of_samples(), dtype=np.float32)
        sr = audio_file.frame_rate
        chroma = librosa.feature.chroma_stft(y=y, sr=sr).T
        if chroma.size == 0:
            return np.zeros((1, 12))
        return chroma


class SpectralContrastExtractor:
    def extract_feature(self, audio_file):
        y = np.array(audio_file.get_array_of_samples(), dtype=np.float32)
        sr = audio_file.frame_rate
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr).T
        if spectral_contrast.size == 0:
            return np.zeros((1, 7))
        return spectral_contrast
