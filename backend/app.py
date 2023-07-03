from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import moviepy.editor as mp
from moviepy.editor import *
from flask_cors import CORS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/Downloads/'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# create a speech recognition object
r = sr.Recognizer()

# Route to handle audio extraction from video
@app.route('/extract-audio', methods=['POST'])
def extract_audio():
    try:
        video_url = request.json.get('videoURL')
        if video_url:
            # Download the video file from the provided URL
            video_clip = VideoFileClip(video_url)
            # Extract the audio
            audio_clip = video_clip.audio
            # Generate a unique filename for the extracted audio
            audio_filename = 'extracted_audio.mp3'
            # Save the audio to the file
            audio_clip.write_audiofile(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

            # Return the filename or any other relevant data
            return jsonify({'audioFile': f"{request.host_url}download/{audio_filename}"})
        else:
            return jsonify({'error': 'Missing videoURL parameter'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to handle audio file download
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})



# Function to generate captions for a video
def generate_captions(video_path):
    video_clip = mp.VideoFileClip(video_path)
    audio_clip = video_clip.audio

    # Export the audio to a temporary file
    audio_filename = "temp_audio.wav"
    audio_clip.write_audiofile(audio_filename)

    # Load the audio file
    audio = AudioSegment.from_wav(audio_filename)

    # Split the audio on silence
    chunks = split_on_silence(
        audio,
        min_silence_len=500,
        silence_thresh=-40,
        keep_silence=500
    )

    captions = []

    for chunk in chunks:
        # Export the chunk as a WAV file for speech recognition
        chunk.export("temp_chunk.wav", format="wav")

        # Perform speech recognition on the chunk
        with sr.AudioFile("temp_chunk.wav") as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio)
                captions.append(text)
            except sr.UnknownValueError:
                print("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Speech Recognition service; {0}".format(e))

    # Remove the temporary files
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
    if os.path.exists("temp_chunk.wav"):
        os.remove("temp_chunk.wav")

    return captions

# Route to handle caption generation
@app.route('/generate-captions', methods=['POST'])
def handle_caption_generation():
    video_url = request.json['videoURL']
    
    try:
        captions = generate_captions(video_url)
        return jsonify({'captions': captions})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()
