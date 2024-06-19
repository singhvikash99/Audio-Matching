import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vocalextraction import VocalExtractor
from featureextractor import MFCCExtractor, TempoExtractor, ChromaExtractor, SpectralContrastExtractor

class ComputeSimilarityFeatures:
    def __init__(self, songs_dir, threshold=0.81):
        self.songs_dir = songs_dir
        self.threshold = threshold
        self.vocal_extractor = VocalExtractor()
        self.mfcc_extractor = MFCCExtractor()
        self.tempo_extractor = TempoExtractor()
        self.chroma_extractor = ChromaExtractor()
        self.spectral_contrast_extractor = SpectralContrastExtractor()



    def compute_similarity(self, feature1, feature2):
        if feature1.shape[0] == 0 or feature2.shape[0] == 0:
            return 0
        return cosine_similarity(feature1, feature2)[0, 0]

    def compute_similarity_segments(self, clip_audio, song_audio):
        segment_duration_ms = 10000
        clip_segments = [clip_audio[i:i + segment_duration_ms] for i in range(0, len(clip_audio), segment_duration_ms)]
        song_segments = [song_audio[i:i + segment_duration_ms] for i in range(0, len(song_audio), segment_duration_ms)]
        similarities = []

        for clip_segment, song_segment in zip(clip_segments, song_segments):
            if len(clip_segment) < segment_duration_ms or len(song_segment) < segment_duration_ms:
                continue

            mfcc_clip = self.mfcc_extractor.extract_feature(clip_segment)
            mfcc_song = self.mfcc_extractor.extract_feature(song_segment)
            tempo_clip = self.tempo_extractor.extract_feature(clip_segment)
            tempo_song = self.tempo_extractor.extract_feature(song_segment)
            chroma_clip = self.chroma_extractor.extract_feature(clip_segment)
            chroma_song = self.chroma_extractor.extract_feature(song_segment)
            spectral_contrast_clip = self.spectral_contrast_extractor.extract_feature(clip_segment)
            spectral_contrast_song = self.spectral_contrast_extractor.extract_feature(song_segment)

            similarity_mfcc = self.compute_similarity(mfcc_clip, mfcc_song)
            similarity_chroma = self.compute_similarity(chroma_clip, chroma_song)
            similarity_spectral_contrast = self.compute_similarity(spectral_contrast_clip, spectral_contrast_song)

            tempo_similarity = 1 - abs(tempo_clip - tempo_song) / max(tempo_clip, tempo_song) if max(tempo_clip, tempo_song) != 0 else 0

            avg_similarity = (similarity_mfcc + similarity_chroma + similarity_spectral_contrast + tempo_similarity) / 4

            similarities.append(avg_similarity)

        if len(similarities) == 0:
            return 0

        return np.mean(similarities)

    def match_clip_with_songs(self, clip_file):
        try:
            clip_audio = self.vocal_extractor.extract_vocals(clip_file)
            
        except Exception as e:
            print(f"Error extracting vocals from clip '{clip_file}': {e}")
            return "No match found", -1

        max_similarity_score = -1
        best_match_song = None
        match_found = False  

        for song_file in os.listdir(self.songs_dir):
            song_path = os.path.join(self.songs_dir, song_file)
            try:
                song_audio = self.vocal_extractor.extract_vocals(song_path)
            except Exception as e:
                print(f"Error extracting vocals from song '{song_file}': {e}")
                continue

            avg_similarity = self.compute_similarity_segments(clip_audio, song_audio)

            if avg_similarity >= self.threshold and avg_similarity > max_similarity_score:
                max_similarity_score = avg_similarity
                best_match_song = song_file
                match_found = True

        if not match_found:
            return "No match found", -1

        return best_match_song, max_similarity_score

