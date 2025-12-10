# BugX - API Key Rotation for Quota Management

## Problem
When using the Google Gemini API with the free tier, you hit quota limits (5 requests per minute). The application would retry indefinitely and fail.

## Solution
Implemented automatic API key rotation that switches to alternate API keys when a quota error (429) is encountered.

## Setup

### 1. Add Multiple API Keys to `.env`

Create or update your `.env` file:

```env
# Primary API Key
GEMINI_API_KEY=your_primary_api_key_here

# Alternate API Keys (comma-separated)
# Add as many keys as you have available
GEMINI_API_KEYS_ALTERNATE=key1,key2,key3,key4,key5
```

### 2. How It Works

1. The application starts with the primary API key (`GEMINI_API_KEY`)
2. If a 429 quota error is encountered, the app automatically rotates to the next available key
3. Each API key gets its own quota, allowing the application to continue working
4. The system tries all available keys before giving up

### 3. Configuration in Code

The key rotation logic is handled in `config.py`:
- `get_api_key()` - Gets the current active API key
- `rotate_api_key()` - Rotates to the next available key
- `get_all_api_keys()` - Returns all configured keys

The runner function in `main.py` automatically handles:
- Catching quota errors (429, "quota exceeded", "ResourceExhausted")
- Rotating to alternate keys
- Retrying with the new key
- Reporting if all keys are exhausted

## Benefits

✅ Automatic failover between multiple API keys  
✅ No manual intervention needed  
✅ Graceful error handling  
✅ Works with any number of API keys  
✅ Maintains agent state across key rotations  

## Example Output

```
Starting Agent...
moved to: E:\-BugX\Test_Project

[API QUOTA EXCEEDED] Rotating to alternate API key (attempt 2/5)...
[INFO] Now using API key: sk_xxx...
```

## Generating Multiple API Keys

To get multiple Gemini API keys:
1. Go to https://ai.google.dev/
2. Sign in with your Google account
3. Create multiple projects (each gets its own quota)
4. Generate an API key for each project
5. Add them all to `GEMINI_API_KEYS_ALTERNATE` in your `.env`

## Notes

- The primary key + all alternate keys should be added
- Keys rotate in order (1 → 2 → 3 → 1)
- Each key has its own free tier quota (5 req/min)
- With 5 keys, you effectively get 25 requests per minute
