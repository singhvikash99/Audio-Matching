import os
import numpy as np
import librosa
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

class FastDTWProcessor:
    def __init__(self, clips_dir, songs_dir):
        self.clips_dir = clips_dir
        self.songs_dir = songs_dir

    def extract_mfcc(self, audio_file):
        y, sr = librosa.load(audio_file)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return mfcc

    def compare_audio(self, clip_file, song_file):
        mfcc_clip = self.extract_mfcc(clip_file)
        mfcc_song = self.extract_mfcc(song_file)

        distance, path = fastdtw(mfcc_clip.T, mfcc_song.T, dist=euclidean)
        normalized_distance = distance / len(path)

        return normalized_distance

    def process_clips(self):
        clip_files = [os.path.join(self.clips_dir, filename) for filename in os.listdir(self.clips_dir) if filename.endswith('.mp3')]
        song_files = [os.path.join(self.songs_dir, filename) for filename in os.listdir(self.songs_dir) if filename.endswith('.mp3')]

        results = {}
        for clip_file in clip_files:
            clip_name = os.path.basename(clip_file)
            min_distance = float('inf')
            best_match = None
            for song_file in song_files:
                song_name = os.path.basename(song_file)
                dtw_distance = self.compare_audio(clip_file, song_file)
                if dtw_distance < min_distance:
                    min_distance = dtw_distance
                    best_match = song_name
            if min_distance < 90:
                results[clip_name] = best_match
            else:
                results[clip_name] = "No Match found"
        
        return results
