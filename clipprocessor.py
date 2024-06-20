import subprocess
import os
from pathlib import Path
from database import DatabaseHandler
from fingerprint import FingerprintHandler
from computesimilarity import ComputeSimilarityFeatures
from featureextractor import HashingHelper
import sqlite3


class ClipProcessor:
    def __init__(self, file_path, songs_dir):
        self.file_path = file_path
        self.songs_dir = songs_dir
        self.database_handler = DatabaseHandler()
        self.fingerprint_handler = FingerprintHandler()
        self.similarity_features_computer = ComputeSimilarityFeatures(self.songs_dir)

    def process_clips(self):
        cursor = self.database_handler.connect()
        clip_file = Path(self.file_path)
        clip_name = clip_file.name
        matching_timestamps = {}

        try:
            duration = self.get_clip_duration(clip_file)
            for start_time in range(0, duration, 12):
                clip_part = clip_file.with_suffix(f".part{start_time}.mp3")
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        str(clip_file),
                        "-ss",
                        str(start_time),
                        "-t",
                        "12",
                        str(clip_part),
                    ]
                )
                fingerprint = self.fingerprint_handler.generate_fingerprint(clip_part)
                match = self.find_match(cursor, fingerprint)
                if match:
                    song_name = match[1]
                    start_timestamp = match[3]
                    end_timestamp = self.add_timestamps(
                        start_timestamp, self.calculate_clip_length(clip_part)
                    )
                    if song_name in matching_timestamps:
                        matching_timestamps[song_name].append(
                            (start_timestamp, end_timestamp)
                        )
                    else:
                        matching_timestamps[song_name] = [
                            (start_timestamp, end_timestamp)
                        ]
                os.remove(clip_part)

            if matching_timestamps:
                merged_timestamps = {}
                for song_name, timestamps in matching_timestamps.items():
                    merged = []
                    if timestamps:
                        timestamps.sort(key=lambda x: x[0])
                        start, end = timestamps[0]
                        for i in range(1, len(timestamps)):
                            next_start, next_end = timestamps[i]
                            start_seconds = self.convert_to_seconds(start)
                            end_seconds = self.convert_to_seconds(end)
                            next_start_seconds = self.convert_to_seconds(next_start)
                            if next_start_seconds - end_seconds <= 15:
                                end = next_end
                            else:
                                merged.append((start, end))
                                start, end = next_start, next_end
                        merged.append((start, end))
                    merged_timestamps[song_name] = merged

                result = {}
                for song_name, timestamps in merged_timestamps.items():
                    if timestamps:
                        filtered_timestamps = [
                            (start, end)
                            for start, end in timestamps
                            if (
                                self.convert_to_seconds(end)
                                - self.convert_to_seconds(start)
                            )
                            >= 15
                        ]
                        if filtered_timestamps:
                            result[song_name] = [
                                f"{start} to {end}"
                                for start, end in filtered_timestamps
                            ]

                if result:
                    return {clip_name: result}

            best_match_song, max_similarity_score = (
                self.similarity_features_computer.match_clip_with_songs(str(clip_file))
            )
            if best_match_song:
                return {
                    clip_name: {
                        best_match_song: f"Best match with similarity score {max_similarity_score}"
                    }
                }
            else:
                return {clip_name: "No match found for the provided clip."}

        except Exception as e:
            print("81")
            return {"error": str(e)}
        finally:
            self.database_handler.close()

    def get_clip_duration(self, clip_file):
        duration_output = subprocess.check_output(
            [
                "ffprobe",
                "-i",
                str(clip_file),
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

    def find_match(self, cursor, fingerprint):
        fingerprint_str = ",".join(map(str, fingerprint))
        fingerprint_elements = fingerprint_str.split(",")

        try:
            cursor.execute("SELECT * FROM fingerprints")
            rows = cursor.fetchall()

            for row in rows:
                fingerprint_in_db = row[
                    4
                ]  
                hashed_fingerprint = HashingHelper.decode(fingerprint_in_db)

                for element in fingerprint_elements:
                    if element in hashed_fingerprint:
                        return row

        except sqlite3.Error as e:
            print("SQLite error:", e)
        except Exception as e:
            print("Error:", e)

    def add_timestamps(self, start_timestamp, clip_length):
        total_seconds = sum(
            int(t.split(":")[i]) * (60 ** (1 - i))
            for i in range(2)
            for t in (start_timestamp, clip_length)
        )
        return f"{total_seconds // 60}:{total_seconds % 60:02d}"

    def calculate_clip_length(self, clip_part):
        duration_output = subprocess.check_output(
            [
                "ffprobe",
                "-i",
                str(clip_part),
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ]
        )
        duration = float(duration_output.strip())
        duration_minutes = int(duration) // 60
        duration_seconds = int(duration) % 60
        duration_format = f"{duration_minutes}:{duration_seconds:02d}"
        return duration_format

    def convert_to_seconds(self, timestamp):
        minutes, seconds = map(int, timestamp.split(":"))
        return minutes * 60 + seconds
