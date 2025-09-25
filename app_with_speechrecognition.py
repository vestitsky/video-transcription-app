import os
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import speech_recognition as sr
from pydub import AudioSegment
import io

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize speech recognizer
recognizer = sr.Recognizer()

def get_language_name(language_code):
    """Get human-readable language name"""
    languages = {
        'auto': 'Auto-detect',
        'ru-RU': 'Russian',
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'es-ES': 'Spanish',
        'fr-FR': 'French',
        'de-DE': 'German',
        'it-IT': 'Italian',
        'pt-BR': 'Portuguese',
        'ja-JP': 'Japanese',
        'ko-KR': 'Korean',
        'zh-CN': 'Chinese',
        'ar-SA': 'Arabic',
        'hi-IN': 'Hindi',
        'tr-TR': 'Turkish',
        'nl-NL': 'Dutch'
    }
    return languages.get(language_code, language_code)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print(f"[DEBUG] Upload request received. Files: {list(request.files.keys())}")

        if 'file' not in request.files:
            print("[DEBUG] No file in request")
            return jsonify({'error': 'No file selected'}), 400

        file = request.files['file']
        selected_language = request.form.get('language', 'auto')
        print(f"[DEBUG] File received: {file.filename}, size: {file.content_length}")
        print(f"[DEBUG] Selected language: {selected_language}")

        if file.filename == '':
            print("[DEBUG] Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"[DEBUG] Saving file to: {file_path}")
            file.save(file_path)

            print(f"[DEBUG] File saved successfully. Starting processing thread with language: {selected_language}")
            threading.Thread(target=process_video, args=(file_path, selected_language)).start()

            return jsonify({'message': 'File uploaded successfully', 'filename': filename, 'language': selected_language})

    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

def process_video(video_path, selected_language='auto'):
    try:
        print(f"[DEBUG] Starting video processing: {video_path} with language: {selected_language}")
        socketio.emit('status', {'message': f'Extracting audio from video... (Language: {get_language_name(selected_language)})'})

        if not MOVIEPY_AVAILABLE:
            print("[ERROR] MoviePy not available")
            socketio.emit('error', {'message': 'MoviePy not available. Please install moviepy to process videos.'})
            return

        print(f"[DEBUG] MoviePy available, proceeding with audio extraction")

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            # Extract audio using moviepy
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
            audio.close()
            video.close()

            socketio.emit('status', {'message': 'Audio extracted. Converting for recognition...'})

            # Convert audio for speech recognition
            audio_segment = AudioSegment.from_wav(temp_audio.name)

            # Convert to format suitable for speech recognition (mono, 16kHz)
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)

            print(f"[DEBUG] Audio segment loaded. Length: {len(audio_segment)}ms")
            socketio.emit('status', {'message': f'Starting transcription with Google Speech Recognition ({get_language_name(selected_language)})...'})

            # Process audio in chunks for better results
            chunk_length_ms = 30000  # 30 seconds
            full_text = ""
            total_chunks = (len(audio_segment) + chunk_length_ms - 1) // chunk_length_ms
            print(f"[DEBUG] Will process {total_chunks} chunks of {chunk_length_ms/1000}s each using language: {selected_language}")

            for i, chunk_start_ms in enumerate(range(0, len(audio_segment), chunk_length_ms)):
                chunk_end_ms = min(chunk_start_ms + chunk_length_ms, len(audio_segment))
                chunk = audio_segment[chunk_start_ms:chunk_end_ms]

                print(f"[DEBUG] Processing chunk {i+1}/{total_chunks} ({chunk_start_ms//1000}-{chunk_end_ms//1000}s)")
                socketio.emit('status', {'message': f'Processing chunk {i+1}/{total_chunks} ({chunk_start_ms//1000}-{chunk_end_ms//1000}s)...'})

                # Export chunk to memory
                print(f"[DEBUG] Exporting chunk {i+1} to memory...")
                chunk_io = io.BytesIO()
                chunk.export(chunk_io, format="wav")
                chunk_io.seek(0)
                print(f"[DEBUG] Chunk {i+1} exported, size: {len(chunk_io.getvalue())} bytes")

                try:
                    # Recognize speech using Google Web Speech API
                    print(f"[DEBUG] Loading chunk {i+1} into speech recognizer...")
                    with sr.AudioFile(chunk_io) as source:
                        chunk_audio = recognizer.record(source)
                    print(f"[DEBUG] Audio loaded for chunk {i+1}")

                    # Use selected language or auto-detect
                    if selected_language == 'auto':
                        # Try Russian first, then English (legacy behavior)
                        print(f"[DEBUG] Auto-detect mode: trying Russian first for chunk {i+1}")
                        try:
                            text = recognizer.recognize_google(chunk_audio, language="ru-RU")
                            language = "ru-RU"
                            print(f"[DEBUG] Russian recognition successful for chunk {i+1}: '{text[:50]}...'")
                        except sr.UnknownValueError:
                            print(f"[DEBUG] Russian recognition failed, trying English for chunk {i+1}")
                            try:
                                text = recognizer.recognize_google(chunk_audio, language="en-US")
                                language = "en-US"
                                print(f"[DEBUG] English recognition successful for chunk {i+1}: '{text[:50]}...'")
                            except sr.UnknownValueError:
                                text = "[неразборчиво]"
                                language = "unknown"
                                print(f"[DEBUG] No speech recognized in chunk {i+1}")
                        except Exception as e:
                            print(f"[DEBUG] Russian recognition error for chunk {i+1}: {str(e)}")
                            try:
                                text = recognizer.recognize_google(chunk_audio, language="en-US")
                                language = "en-US"
                                print(f"[DEBUG] English recognition successful for chunk {i+1}: '{text[:50]}...'")
                            except Exception as e2:
                                text = "[ошибка распознавания]"
                                language = "error"
                                print(f"[DEBUG] All recognition failed for chunk {i+1}: {str(e2)}")
                    else:
                        # Use specific language
                        print(f"[DEBUG] Using specific language {selected_language} for chunk {i+1}")
                        try:
                            text = recognizer.recognize_google(chunk_audio, language=selected_language)
                            language = selected_language
                            print(f"[DEBUG] {selected_language} recognition successful for chunk {i+1}: '{text[:50]}...'")
                        except sr.UnknownValueError:
                            text = "[неразборчиво]"
                            language = "unknown"
                            print(f"[DEBUG] No speech recognized in {selected_language} for chunk {i+1}")
                        except Exception as e:
                            text = "[ошибка распознавания]"
                            language = "error"
                            print(f"[DEBUG] {selected_language} recognition failed for chunk {i+1}: {str(e)}")

                    if text and text not in ["[неразборчиво]", "[ошибка распознавания]"]:
                        full_text += text + " "
                        print(f"[DEBUG] Added text from chunk {i+1} to full result")

                        # Send real-time update
                        socketio.emit('transcription_segment', {
                            'text': text + " ",
                            'start': chunk_start_ms / 1000,
                            'end': chunk_end_ms / 1000
                        })
                    else:
                        print(f"[DEBUG] Skipping empty/unrecognized chunk {i+1}")

                except Exception as e:
                    print(f"[ERROR] Error processing chunk {i+1}: {str(e)}")
                    socketio.emit('status', {'message': f'Error processing chunk {i+1}: {str(e)}'})
                    continue

            # Send final result
            if full_text.strip():
                socketio.emit('transcription_complete', {
                    'text': full_text.strip(),
                    'language': language if 'language' in locals() else 'mixed'
                })
                socketio.emit('status', {'message': 'Transcription completed!'})
            else:
                socketio.emit('error', {'message': 'Could not transcribe audio. Please check if the audio contains clear speech.'})

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