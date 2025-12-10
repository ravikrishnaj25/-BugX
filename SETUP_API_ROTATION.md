# Setup Guide for API Key Rotation

## Quick Start

### Step 1: Update Your `.env` File

Add your API keys to `.env`:

```env
GEMINI_API_KEY=your_primary_key_here
GEMINI_API_KEYS_ALTERNATE=key2,key3,key4,key5
```

### Step 2: How to Get Multiple Gemini API Keys

1. **Create multiple Google Cloud projects:**
   - Go to https://console.cloud.google.com/
   - Create 5 separate projects (each gets free tier quota)

2. **Enable Gemini API for each project:**
   - In each project, go to APIs & Services → Enable APIs
   - Search for "Generative Language API" and enable it

3. **Generate API keys:**
   - For each project, go to APIs & Services → Credentials
   - Create an API key
   - Copy and paste into your `.env`

### Step 3: Run Your Application

```powershell
python main.py
```

## What Happens When Quota is Hit

1. ❌ First key hits quota (429 error)
2. 🔄 System automatically rotates to next key
3. ✅ Operation retries with new key
4. Repeat for each configured key until one succeeds

## Features Implemented

✅ **Automatic Rotation** - Switches keys without manual intervention  
✅ **Quota Error Detection** - Catches 429, "quota exceeded", "ResourceExhausted"  
✅ **Multiple Key Support** - Works with any number of keys  
✅ **Graceful Degradation** - Clear error if all keys are exhausted  
✅ **Transparent** - Agent state is preserved across key rotations  

## Configuration Details

### Files Modified

1. **config.py**
   - `get_api_key()` - Get current active key
   - `rotate_api_key()` - Switch to next key
   - `get_all_api_keys()` - List all keys

2. **main.py**
   - `run_bugx_agent()` - Enhanced with retry logic for quota errors
   - `create_llm_with_current_key()` - Creates LLM with active key
   - `create_agent_with_current_llm()` - Creates agent with current LLM

### How Rotation Works

```
Initial State:
  API Key Index: 0 (Primary Key)

After First Quota Error:
  API Key Index: 1 (First Alternate)
  
After Second Quota Error:
  API Key Index: 2 (Second Alternate)
  
...and so on, cycling through all available keys
```

## Troubleshooting

**Error: "No API keys configured"**
- Check your `.env` file
- Ensure `GEMINI_API_KEY` is set

**Error: "All API keys exhausted quota limits"**
- All your API keys have hit their quotas
- Wait for quota to reset (usually 1 minute)
- Or add more API keys to `.env`

**Keys not rotating**
- Check if the error message contains "429", "quota", or "ResourceExhausted"
- The system only rotates on quota errors, not other errors
