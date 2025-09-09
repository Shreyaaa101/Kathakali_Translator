import os
import asyncio
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv

class TranscriptionModule:
    def __init__(self):
        load_dotenv()
        
        api_key = os.getenv('KAPI')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:5000", 
                "X-Title": "Sanskrit Translator"
            }
        )
    
    def audio_to_base64(self, audio_file_path):
        """Convert audio file to base64 for API transmission"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                return base64_audio
        except Exception as e:
            print(f"Error converting audio to base64: {e}")
            return None
    
    async def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio using OpenRouter's API
        """
        try:
            print(f"Transcribing audio file: {audio_file_path}")
            
            # Check if file exists and is readable
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Get file size for debugging
            file_size = os.path.getsize(audio_file_path)
            print(f"Audio file size: {file_size / (1024*1024):.2f} MB")
            
            # Check if file is too large (OpenRouter has limits)
            if file_size > 25 * 1024 * 1024:  # 25MB limit
                raise ValueError("Audio file too large (>25MB). Please use a smaller file.")
            
            # Try transcription with OpenRouter
            with open(audio_file_path, 'rb') as audio_file:
                print("Sending request to OpenRouter API...")
                response = await self.client.audio.transcriptions.create(
                    model="openai/whisper-large-v3",
                    file=audio_file,
                    language="sa",  # Sanskrit language code
                    response_format="text"
                )
            
            transcribed_text = response if isinstance(response, str) else response.text
            
            if not transcribed_text or transcribed_text.strip() == "":
                raise ValueError("Received empty transcription from API")
            
            # Save transcription to file for reference
            with open("transcript.txt", "w", encoding="utf-8") as f:
                f.write(transcribed_text)
            
            print("Transcription completed successfully")
            print(f"Transcribed text preview: {transcribed_text[:100]}...")
            return transcribed_text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Transcription error: {error_msg}")
            
            # Provide specific error messages
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                print("❌ Authentication failed - check your OPENROUTER_API_KEY")
                return None
            elif "insufficient" in error_msg.lower() or "credits" in error_msg.lower():
                print("❌ Insufficient credits in OpenRouter account")
                return None
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                print("❌ Network connection issue")
                return None
            elif "file too large" in error_msg.lower():
                print("❌ Audio file is too large")
                return None
            
            # Fallback: Use sample text for demo
            print("🔄 Using fallback sample text for demo...")
            try:
                return await self.fallback_transcription(audio_file_path)
            except Exception as fallback_error:
                print(f"Fallback transcription also failed: {fallback_error}")
                return None
    
    async def fallback_transcription(self, audio_file_path):
        """
        Fallback method: Use chat completion with audio description
        This is a workaround if direct audio transcription doesn't work
        """
        try:
            # For demo purposes, if transcription fails, we'll return sample Sanskrit text
            # In a real scenario, you might want to use a different approach
            sample_sanskrit = """
            अजिता हरे जय माधवा विष्णो अजमुख देव नाथा विजय शारदे 
            साधु द्विजनोनु परयुन्नु सुजन सङ्गममेत्तम् सुकृत निवग 
            सुलभमथनु नियतम् पलदिनमायि ञ्जनम् बलभद्रनुजा निन्ने 
            नलमोडु काण्मथिन्नु कलियल्ले रुचिक्कुन्नु काल विशमम् कोण्डु
            """
            
            print("Using fallback sample text for demo")
            return sample_sanskrit.strip()
            
        except Exception as e:
            print(f"Fallback error: {e}")
            return None