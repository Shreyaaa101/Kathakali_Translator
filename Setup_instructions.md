# Real-Time Sanskrit Translation Setup Guide

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create templates directory
mkdir templates

# Set environment variable (if not already set)
export OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 2. Environment Setup

Since you already have `OPENROUTER_API_KEY` set in your environment variables, the app should work immediately. 

If you prefer using a `.env` file, create one:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your OpenRouter API key from: https://openrouter.ai/

### 3. File Structure

```
project/
├── main.py                 # Main Flask-SocketIO server
├── transcription_module.py # OpenRouter transcription module  
├── translation_module.py   # OpenRouter translation module
├── templates/
│   └── index.html          # Frontend interface
├── requirements.txt        # Dependencies
├── .env                   # API keys (optional)
├── your-audio-files.*     # Place your audio files here
└── transcript.txt         # Generated transcript (auto-created)
```

### 4. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:5000`

## 🎯 How It Works

### Real-Time Flow:
1. **Upload/Select Audio**: Choose from existing files or upload new ones
2. **Start Processing**: Click "Start Translation" in the web interface  
3. **API Transcription**: OpenRouter's Whisper API transcribes the audio
4. **Sentence Splitting**: Text is split into meaningful sentences
5. **API Translation**: Each sentence is translated using Claude/GPT via OpenRouter
6. **Live Display**: Only one sentence pair shows at a time, creating a real-time effect

### Supported Audio Formats:
- MP3, WAV, M4A, AAC, OGG, FLAC

### API Models Used:
- **Transcription**: `openai/whisper-large-v3` via OpenRouter
- **Translation**: `anthropic/claude-3.5-sonnet` (fallback: `openai/gpt-4o-mini`)

## 🎛️ Features

### Web Interface:
- **File Selection**: Dropdown of available audio files
- **File Upload**: Drag & drop or click to upload new audio
- **Real-time Processing**: Live status updates
- **Sentence Display**: One sentence at a time with smooth transitions
- **Progress Tracking**: Visual progress bar
- **Controls**: Start/Stop processing anytime

## 🔧 Troubleshooting

### Common Issues:

1. **API Key Issues**: 
   - Verify `OPENROUTER_API_KEY` is set: `echo $OPENROUTER_API_KEY`
   - Check API quota and billing status on OpenRouter

2. **Audio File Issues**:
   - Ensure supported format (MP3, WAV, etc.)
   - Check file isn't corrupted
   - File size limits apply (check OpenRouter limits)

3. **No Audio Files Shown**:
   - Place audio files in the project root directory
   - Click "Refresh" button to reload file list
   - Check file permissions

4. **WebSocket Issues**:
   - Refresh browser
   - Check browser console for errors
   - Ensure port 5000 isn't blocked

### Performance Notes:

- **Processing Time**: Depends on audio length and API response times
- **API Costs**: Each transcription and translation uses API credits
- **File Limits**: Large files may take longer or hit API limits
- **Network**: Stable internet required for all API calls

## 🎨 Customization

### Backend Models:
- Change transcription model in `transcription_module.py`
- Update translation model in `translation_module.py`
- Modify sentence splitting logic in `main.py`

### Frontend:
- Adjust delay between sentences
- Customize UI colors and animations
- Add new audio format support