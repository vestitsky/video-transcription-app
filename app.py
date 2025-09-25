import os
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
# import whisper  # Will install later
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

model = None

def load_whisper_model():
    global model
    if model is None:
        try:
            import whisper
            model = whisper.load_model("base")
        except ImportError:
            model = "mock"  # Mock for testing without whisper
    return model

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        threading.Thread(target=process_video, args=(file_path,)).start()

        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

def process_video(video_path):
    try:
        socketio.emit('status', {'message': 'Extracting audio from video...'})

        if not MOVIEPY_AVAILABLE:
            socketio.emit('error', {'message': 'MoviePy not available. Please install moviepy to process videos.'})
            return

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
            audio.close()
            video.close()

            socketio.emit('status', {'message': 'Audio extracted. Starting transcription...'})

            whisper_model = load_whisper_model()

            if whisper_model == "mock":
                # Mock transcription for testing
                import time
                socketio.emit('status', {'message': 'Using mock transcription (Whisper not installed)'})
                time.sleep(2)
                mock_text = "This is a mock transcription. Install openai-whisper for actual speech recognition."
                socketio.emit('transcription_complete', {
                    'text': mock_text,
                    'language': 'en'
                })
                socketio.emit('transcription_segment', {
                    'text': mock_text,
                    'start': 0,
                    'end': 5
                })
            else:
                result = whisper_model.transcribe(
                    temp_audio.name,
                    language=None,
                    task='transcribe',
                    verbose=False
                )

                detected_language = result.get('language', 'unknown')
                socketio.emit('status', {'message': f'Detected language: {detected_language}'})

                full_text = result['text']
                socketio.emit('transcription_complete', {
                    'text': full_text,
                    'language': detected_language
                })

                for segment in result['segments']:
                    socketio.emit('transcription_segment', {
                        'text': segment['text'],
                        'start': segment['start'],
                        'end': segment['end']
                    })

            os.unlink(temp_audio.name)

    except Exception as e:
        socketio.emit('error', {'message': f'Error processing video: {str(e)}'})

    finally:
        try:
            os.remove(video_path)
        except:
            pass

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)