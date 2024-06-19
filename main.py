from flask import Flask, render_template, request, jsonify
from utils import list_uploaded_songs
import os
import subprocess
from database import DatabaseHandler 
from songprocessor import SongProcessor
from clipprocessor import ClipProcessor
from tasks import process_clips_task



app = Flask(__name__)
db_handler = DatabaseHandler()

os.makedirs("./songs", exist_ok=True)
os.makedirs("./clips", exist_ok=True)
os.makedirs("./demucs_output", exist_ok=True)

# def convert_to_192kbps(input_file):
#     output_file = os.path.splitext(input_file)[0] + "_192kbps.mp3"
#     command = ['ffmpeg', '-i', input_file, '-b:a', '192k', '-y', output_file]
#     subprocess.run(command)
#     return output_file


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/list_songs/", methods=["GET"])
def list_songs():
    song_names =list_uploaded_songs()
    return render_template("song_list.html", song_names=song_names)


@app.route("/upload_song/", methods=["POST"])
def upload_song():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No selected file"})

    if uploaded_file:
        uploaded_file_path = "./songs/" + uploaded_file.filename
        uploaded_file.save(uploaded_file_path)

        try:
            song_processor = SongProcessor()

            song_processor.process_song(uploaded_file_path)

            # os.remove(uploaded_file_path)

            return jsonify({"success": "Song uploaded and processed successfully"})
        except Exception as e:
            return jsonify({"error": f"Error processing song: {str(e)}"})


@app.route("/match_song/", methods=["POST"])
def match_song():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No selected file"})

    uploaded_file_path = "./clips/" + uploaded_file.filename
    uploaded_file.save(uploaded_file_path)

    try:
        songs_dir = "./songs"  
        process_clips_task.delay(uploaded_file_path, songs_dir)  
        return jsonify("Processing initiated. Results will be sent via email on completion.")

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/clear_songs/", methods=["DELETE", "GET"])
def clear_songs():
    success, message = db_handler.clear_songs()

    if success:
        return jsonify({"success": message})
    else:
        return jsonify({"error": message})


if __name__ == "__main__":
    app.run(debug=True)
