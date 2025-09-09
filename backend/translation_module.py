import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

class TranslationModule:
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
    
    async def translate_sentence(self, sanskrit_text):
        """
        Translate Sanskrit text to English using OpenRouter API
        """
        try:
            print(f"Translating: {sanskrit_text[:50]}...")
            
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert Sanskrit translator specializing in devotional and spiritual texts. 

Your task:
1. Translate the given Sanskrit text to natural, flowing English
2. Focus on the devotional and spiritual meaning
3. Keep translations concise but meaningful
4. If the text appears to be garbled or unclear, provide the best possible interpretation
5. Respond with ONLY the English translation, no explanations

Context: This is likely devotional content related to Hindu deities like Krishna, Vishnu, or other divine beings."""
                    },
                    {
                        "role": "user", 
                        "content": f"Translate this Sanskrit text to English: {sanskrit_text}"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            print(f"Translation: {translation}")
            return translation
            
        except Exception as e:
            error_msg = str(e)
            print(f"Translation error: {error_msg}")
            
            # Provide specific error handling
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                print("❌ Authentication failed - check your OPENROUTER_API_KEY")
                return f"Authentication error: {sanskrit_text}"
            elif "insufficient" in error_msg.lower() or "credits" in error_msg.lower():
                print("❌ Insufficient credits in OpenRouter account") 
                return f"Credit error - Original: {sanskrit_text}"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                print("❌ Network connection issue")
                return f"Network error - Original: {sanskrit_text}"
            
            # Try fallback model
            try:
                return await self.fallback_translation(sanskrit_text)
            except Exception as fallback_error:
                print(f"Fallback translation failed: {fallback_error}")
                return f"Translation unavailable: {sanskrit_text}"
    
    async def fallback_translation(self, sanskrit_text):
        """Fallback translation using a different model"""
        try:
            response = await self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Sanskrit translator. Translate the given Sanskrit text to English. Focus on devotional meaning. Respond with only the translation."
                    },
                    {
                        "role": "user",
                        "content": f"Translate: {sanskrit_text}"
                    }
                ],
                max_tokens=150,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Fallback translation error: {e}")
            return f"Unable to translate: {sanskrit_text}"
    
    async def batch_translate(self, sentences):
        """Translate multiple sentences"""
        translations = []
        for sentence in sentences:
            translation = await self.translate_sentence(sentence)
            translations.append(translation)
        return translations