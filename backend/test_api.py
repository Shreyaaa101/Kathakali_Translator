import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_api_connection():
    """Test OpenRouter API connection"""
    load_dotenv()
    
    api_key = os.getenv('KAPI')
    
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key (first 10 chars): {api_key[:10]}...")
    
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY environment variable is not set!")
        print("\nTo fix this:")
        print("1. Get your API key from: https://openrouter.ai/keys")
        print("2. Set it as environment variable:")
        print("   Windows: $env:OPENROUTER_API_KEY='your-key-here'")
        print("   Linux/Mac: export OPENROUTER_API_KEY='your-key-here'")
        return
    
    try:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Sanskrit Translator Test"
            }
        )
        
        print("\n🔄 Testing API connection...")
        
        # Test with a simple translation
        response = await client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working!' in one sentence."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ SUCCESS: {result}")
        print("🎉 API connection is working!")
        
        # Test available models
        print("\n🔍 Testing model availability...")
        try:
            models_response = await client.models.list()
            print(f"✅ Models endpoint accessible, found {len(models_response.data)} models")
        except Exception as e:
            print(f"⚠️  Models endpoint error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. No credits left on OpenRouter account")
        print("3. Network connectivity issues")
        print("4. OpenRouter service temporarily unavailable")
        
        # Check specific error types
        error_str = str(e).lower()
        if "unauthorized" in error_str or "401" in error_str:
            print("\n🔑 Likely cause: Invalid API key")
        elif "insufficient" in error_str or "credits" in error_str:
            print("\n💰 Likely cause: Insufficient credits")
        elif "timeout" in error_str or "connection" in error_str:
            print("\n🌐 Likely cause: Network issue")
        
        return False

if __name__ == "__main__":
    print("🧪 OpenRouter API Connection Test")
    print("=" * 40)
    
    result = asyncio.run(test_api_connection())
    
    if result:
        print("\n✅ All tests passed! Your API should work in the main app.")
    else:
        print("\n❌ Please fix the issues above before running the main app.")