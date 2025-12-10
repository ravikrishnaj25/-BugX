import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Primary API key
google_api = os.environ.get("GEMINI_API_KEY")

# Alternate API keys (comma-separated in environment variable)
# Set GEMINI_API_KEYS_ALTERNATE="key1,key2,key3" in your .env file
alternate_api_keys_str = os.environ.get("GEMINI_API_KEYS_ALTERNATE", "")
alternate_api_keys = [key.strip() for key in alternate_api_keys_str.split(",") if key.strip()]

# Combine all keys
all_api_keys = [google_api] + alternate_api_keys if google_api else alternate_api_keys

# Current API key index for rotation
_current_key_index = 0

def get_api_key():
    """Get the current API key"""
    if not all_api_keys:
        raise ValueError("No API keys configured. Set GEMINI_API_KEY or GEMINI_API_KEYS_ALTERNATE")
    return all_api_keys[_current_key_index]

def rotate_api_key():
    """Rotate to the next available API key"""
    global _current_key_index
    if len(all_api_keys) <= 1:
        raise ValueError("No alternate API keys available for rotation")
    _current_key_index = (_current_key_index + 1) % len(all_api_keys)
    return get_api_key()

def get_all_api_keys():
    """Get all configured API keys"""
    return all_api_keys

llm = genai.Client(api_key=google_api)

def get_prompt_tokens(response):
    return response.usage_metadata.prompt_token_count

def get_response_tokens(response):
    return response.usage_metadata.candidates_token_count

#print(response.text)
#print(get_prompt_tokens(response))
#print(get_response_tokens(response))

