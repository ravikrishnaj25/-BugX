# API Key Rotation - Visual Guide

## 🔄 Rotation Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BugX Agent Execution Start                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Load Configuration          │
            │  • Read GEMINI_API_KEY       │
            │  • Read GEMINI_API_KEYS_ALT  │
            │  • Initialize key index = 0  │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │  Create LLM with Key[0]      │
            │  Create Agent                │
            └──────────────┬───────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │   Attempt Agent Invoke              │
         │   (Make API Call to Gemini)         │
         └─────────────┬───────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    ✅ SUCCESS                   ❌ ERROR
    │                             │
    │                             ▼
    │                    ┌─────────────────────────┐
    │                    │  Check Error Type       │
    │                    │  • 429?                 │
    │                    │  • "quota"?             │
    │                    │  • ResourceExhausted?   │
    │                    └────────┬────────────────┘
    │                             │
    │                ┌────────────┴────────────┐
    │                │                         │
    │                ▼                         ▼
    │          🔄 QUOTA ERROR          ❌ OTHER ERROR
    │          │                       │
    │          ▼                       └──► Return Error
    │    ┌─────────────────────────────┐
    │    │  Check Remaining Keys       │
    │    │  attempt < max_retries?     │
    │    └────────┬────────────────────┘
    │            │
    │    ┌───────┴────────┐
    │    │                │
    │    ▼                ▼
    │  🔄 YES           ❌ NO
    │  │                │
    │  ▼                └──► Return Error
    │  ┌──────────────────────────────┐
    │  │ Rotate Key Index             │
    │  │ index = (index + 1) % total  │
    │  └──────┬───────────────────────┘
    │         │
    │         ▼
    │  ┌──────────────────────────────┐
    │  │ Create New LLM with Key[i]   │
    │  │ Recreate Agent               │
    │  └──────┬───────────────────────┘
    │         │
    │         ▼
    │  ┌──────────────────────────────┐
    │  │ Print Rotation Message       │
    │  │ "[API QUOTA EXCEEDED]        │
    │  │  Rotating to key attempt 2"  │
    │  └──────┬───────────────────────┘
    │         │
    │         └─────► Loop Back to "Attempt Agent Invoke"
    │
    └──────► Return Success Result
```

## 🔀 Key Rotation Sequence

```
Initial State:
┌─────────────────────────────────────────┐
│ Available Keys:  [Key1][Key2][Key3]     │
│ Current Index:    ^0                    │
│ Status: Using Key1                      │
└─────────────────────────────────────────┘

After 1st Quota Error:
┌─────────────────────────────────────────┐
│ Available Keys:  [Key1][Key2][Key3]     │
│ Current Index:            ^1            │
│ Status: Using Key2 (rotated)            │
└─────────────────────────────────────────┘

After 2nd Quota Error:
┌─────────────────────────────────────────┐
│ Available Keys:  [Key1][Key2][Key3]     │
│ Current Index:                  ^2      │
│ Status: Using Key3 (rotated)            │
└─────────────────────────────────────────┘

After 3rd Quota Error (with 3 keys):
┌─────────────────────────────────────────┐
│ Available Keys:  [Key1][Key2][Key3]     │
│ Current Index:    ^0 (cycled back)      │
│ Status: Using Key1 (rotated)            │
└─────────────────────────────────────────┘
```

## 🎯 Error Detection Logic

```
┌─────────────────────────────────────────────────────────────┐
│                  Exception Caught                           │
└──────────────────────┬────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    Check for "429"  Check for    Check for
    in error string  "quota"      "ResourceExhausted"
                     in error     in exception type
                     message
         │             │             │
         └─────────────┼─────────────┘
                       │
                  IF ANY TRUE
                       │
                       ▼
         ┌──────────────────────────┐
         │  QUOTA ERROR DETECTED    │
         │  Proceed with Rotation   │
         └──────────────────────────┘
         
         
                  IF ALL FALSE
                       │
                       ▼
         ┌──────────────────────────┐
         │  OTHER ERROR             │
         │  Return Error Directly   │
         │  (No Rotation)           │
         └──────────────────────────┘
```

## 📊 Quota Management Timeline

```
Time →
Key1: ████████ (5 req/min quota)
Key2: ████████ (5 req/min quota)
Key3: ████████ (5 req/min quota)

When Key1 quota exhausted:
├─ ❌ Key1 blocked
├─ 🔄 Rotate to Key2
└─ ✅ Continue with Key2

When Key2 quota exhausted:
├─ ❌ Key2 blocked
├─ 🔄 Rotate to Key3
└─ ✅ Continue with Key3

After ~1 minute:
Key1: ✅ Quota Reset → Available again
Key2: ✅ Quota Reset → Available again
Key3: ✅ Quota Reset → Available again
```

## 🔧 Configuration Structure

```
.env File:
├─ GEMINI_API_KEY = "sk_xxxx"           (Primary Key)
└─ GEMINI_API_KEYS_ALTERNATE = "sk_yyyy,sk_zzzz"  (Alternates)

config.py:
├─ google_api = "sk_xxxx"
├─ alternate_api_keys = ["sk_yyyy", "sk_zzzz"]
├─ all_api_keys = ["sk_xxxx", "sk_yyyy", "sk_zzzz"]
├─ _current_key_index = 0
├─ get_api_key()        ← Returns all_api_keys[_current_key_index]
├─ rotate_api_key()     ← Increments _current_key_index
└─ get_all_api_keys()   ← Returns full list

main.py:
├─ create_llm_with_current_key()    ← Uses get_api_key()
├─ create_agent_with_current_llm()  ← Uses new LLM
└─ run_bugx_agent()                 ← Orchestrates rotation
    └─ Catches 429 errors
    └─ Calls rotate_api_key()
    └─ Recreates LLM & Agent
    └─ Retries operation
```

## 💡 Example Scenarios

### Scenario 1: Single API Key (No Rotation Possible)
```
Attempt 1: Use Key1
├─ Success → Operation completes ✅
└─ Quota Error → No alternate keys available ❌
   └─ Error: "No alternate API keys available for rotation"
```

### Scenario 2: Multiple Keys - Smooth Operation
```
Attempt 1: Use Key1
├─ Success → Operation completes ✅

Later...
Attempt 1: Use Key1
├─ Quota Error 429
└─ Rotate to Key2

Attempt 2: Use Key2
├─ Success → Operation completes ✅
```

### Scenario 3: Multiple Keys - All Exhausted
```
Attempt 1: Use Key1 → Quota Error
├─ Rotate to Key2

Attempt 2: Use Key2 → Quota Error
├─ Rotate to Key3

Attempt 3: Use Key3 → Quota Error
├─ All keys exhausted ❌
└─ Return Error: "All API keys exhausted quota limits"
```

## 📈 Performance Metrics

```
Throughput with Different Key Counts:

1 Key:   ████ 5 requests/minute
2 Keys:  ████████ 10 requests/minute
3 Keys:  ████████████ 15 requests/minute
5 Keys:  ████████████████████ 25 requests/minute
10 Keys: ████████████████████████████████████████ 50 requests/minute
```

## 🚀 Optimization Opportunities

```
Current Implementation:
├─ Round-robin rotation
├─ Rotate on ANY quota error
└─ No key prioritization

Potential Future Enhancements:
├─ Weighted key selection
├─ Track quota per key
├─ Predict quota exhaustion
├─ Distribute load proactively
└─ Persistent usage statistics
```
