import asyncio
import json
import time
import os
import base64
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import re
from translation_module import TranslationModule
from transcription_module import TranscriptionModule

app = Flask(__name__)
app.config['KAPI'] = 'KAPI'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

class RealTimeTranslator:
    def __init__(self):
        self.translation_module = TranslationModule()
        self.transcription_module = TranscriptionModule()
        self.is_processing = False
        
    def split_into_sentences(self, text):
        """Split text into meaningful sentences/phrases"""
        # Split on common punctuation and natural breaks
        sentences = re.split(r'[।॥\.\!\?]+|(?<=\w)\s+(?=[A-Z])', text.strip())
        # Filter out empty strings and clean up
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
        return sentences
    
    async def process_audio_realtime(self, audio_file_path, delay_per_sentence=3):
        """Process audio file and emit real-time translations"""
        try:
            self.is_processing = True
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                socketio.emit('status', {'message': f'Audio file "{audio_file_path}" not found', 'type': 'error'})
                return
            
            socketio.emit('status', {'message': 'Starting audio transcription...', 'type': 'info'})
            
            # Step 1: Transcribe the audio using OpenRouter API
            transcribed_text = await self.transcription_module.transcribe_audio(audio_file_path)
            
            if not transcribed_text:
                socketio.emit('status', {'message': 'Transcription failed', 'type': 'error'})
                return
            
            socketio.emit('status', {'message': 'Transcription complete! Starting translation...', 'type': 'success'})
            
            # Step 2: Split into sentences
            sentences = self.split_into_sentences(transcribed_text)
            
            if not sentences:
                socketio.emit('status', {'message': 'No sentences found in transcription', 'type': 'error'})
                return
            
            socketio.emit('status', {'message': f'Processing {len(sentences)} sentences...', 'type': 'info'})
            
            # Step 3: Process each sentence with delay
            for i, sentence in enumerate(sentences):
                if not self.is_processing:  # Check if user stopped
                    break
                    
                # Translate the sentence
                socketio.emit('status', {'message': f'Translating sentence {i+1}...', 'type': 'info'})
                translation = await self.translation_module.translate_sentence(sentence)
                
                # Emit the sentence pair
                socketio.emit('sentence_update', {
                    'sanskrit': sentence,
                    'english': translation,
                    'index': i + 1,
                    'total': len(sentences),
                    'progress': ((i + 1) / len(sentences)) * 100
                })
                
                # Wait before next sentence (simulate real-time)
                await asyncio.sleep(delay_per_sentence)
            
            if self.is_processing:
                socketio.emit('status', {'message': 'Translation complete!', 'type': 'success'})
                socketio.emit('processing_complete', {'total_sentences': len(sentences)})
            
        except Exception as e:
            socketio.emit('status', {'message': f'Error: {str(e)}', 'type': 'error'})
        finally:
            self.is_processing = False

# Global translator instance
translator = RealTimeTranslator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle audio file uploads"""
    try:
        if 'audio' not in request.files:
            return {'error': 'No audio file provided'}, 400
        
        file = request.files['audio']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
        
        # Save the uploaded file
        filename = f"uploaded_audio_{int(time.time())}.{file.filename.split('.')[-1]}"
        filepath = os.path.join(os.getcwd(), filename)
        file.save(filepath)
        
        return {'success': True, 'filename': filename}, 200
    
    except Exception as e:
        return {'error': str(e)}, 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'message': 'Connected to server', 'type': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    translator.is_processing = False

@socketio.on('start_processing')
def handle_start_processing(data):
    audio_file = data.get('audio_file', 'chunk_1.wav')
    delay = data.get('delay', 3)  # seconds between sentences
    
    if translator.is_processing:
        emit('status', {'message': 'Processing already in progress', 'type': 'warning'})
        return
    
    # Run the processing in a separate thread
    def run_processing():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(translator.process_audio_realtime(audio_file, delay))
        loop.close()
    
    thread = threading.Thread(target=run_processing)
    thread.daemon = True
    thread.start()
    
    emit('status', {'message': 'Processing started...', 'type': 'info'})

@socketio.on('stop_processing')
def handle_stop_processing():
    translator.is_processing = False
    emit('status', {'message': 'Processing stopped by user', 'type': 'warning'})

@socketio.on('test_connection')
def handle_test():
    emit('status', {'message': 'WebSocket connection working!', 'type': 'success'})

@socketio.on('list_audio_files')
def handle_list_files():
    """List available audio files in the directory"""
    try:
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        audio_files = []
        
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(file)
        
        emit('audio_files_list', {'files': audio_files})
    except Exception as e:
        emit('status', {'message': f'Error listing files: {str(e)}', 'type': 'error'})

if __name__ == '__main__':
    print("Starting Real-Time Sanskrit Translation Server...")
    print("Access the application at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)