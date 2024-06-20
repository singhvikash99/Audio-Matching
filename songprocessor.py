import subprocess
import os
from pathlib import Path
from database import DatabaseHandler
from fingerprint import FingerprintHandler
from featureextractor import HashingHelper


class SongProcessor:
    def __init__(self, database_handler=None, fingerprint_handler=None):
        self.database_handler = database_handler or DatabaseHandler()
        self.fingerprint_handler = fingerprint_handler or FingerprintHandler()

    def process_song(self, song_path):
        song_file = Path(song_path)

        try:
            cursor = self.database_handler.connect()

            self.generate_and_save_fingerprints(cursor, song_file)

            self.database_handler.commit()

        except Exception as e:
            print("Error processing song:", e)
            self.database_handler.rollback()
            raise
        finally:
            self.database_handler.close()

    def generate_and_save_fingerprints(self, cursor, song_file):
        duration = self.get_song_duration(song_file)

        for start_time in range(0, duration, 12):
            song_part = song_file.with_suffix(f".part{start_time}.mp3")
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    str(song_file),
                    "-ss",
                    str(start_time),
                    "-t",
                    "12",
                    str(song_part),
                ]
            )
            fingerprint = self.fingerprint_handler.generate_fingerprint(song_part)
            hashed_fingerprint = HashingHelper.hash_feature(fingerprint)

            if self.fingerprint_handler.fingerprint_exists(cursor, hashed_fingerprint):
                os.remove(song_part)
                continue

            cursor.execute(
                "INSERT INTO fingerprints (song_id, time_offset, timestamp, hashed_fingerprint) VALUES (?, ?, ?, ?)",
                (
                    song_file.stem,
                    start_time,
                    self.format_timestamp(start_time // 60, start_time % 60),
                    hashed_fingerprint,
                ),
            )
            os.remove(song_part)

    def extract_and_save_vocal_features(self, cursor, song_file):
        vocal_segment = self.vocal_extractor.extract_vocals(song_file)

        feature_values = {
            "mfcc": None,
            "tempo": None,
            "chroma": None,
            "spectral_contrast": None,
        }

        for feature_type, extractor in self.feature_extractors.items():
            feature_value = extractor.extract_feature(vocal_segment)
            hashed_feature = HashingHelper.hash_feature(feature_value)

            if not self.feature_exists(cursor, hashed_feature):
                feature_values[feature_type] = hashed_feature

        cursor.execute(
            "INSERT INTO features (song_id, type, mfcc, tempo, chroma, spectral_contrast) VALUES (?, ?, ?, ?, ?, ?)",
            (
                song_file.stem + "_vocals",
                song_file.name + "_vocals",
                feature_values["mfcc"],
                feature_values["tempo"],
                feature_values["chroma"],
                feature_values["spectral_contrast"],
            ),
        )
        self.vocal_extractor.remove_extracted_vocals(song_file)

    def get_song_duration(self, song_file):
        duration_output = subprocess.check_output(
            [
                "ffprobe",
                "-i",
                str(song_file),
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ]
        )
        duration = float(duration_output.strip())
        return int(duration)

    def format_timestamp(self, minutes: int, seconds: int) -> str:
        return f"{minutes}:{seconds:02d}"
