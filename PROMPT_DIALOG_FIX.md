# JavaScript Fix for Agent Run UUID Issue

## Problem
The prompt dialog was failing with a 404 error because `window.agentRunUuid` was `undefined` in the API call URL:
```
POST http://192.168.2.120:5004/agents/api/agent_run/undefined/task/62f35e6c-c0bd-4317-8df6-ea66a50c6d2f/prompt 404 (NOT FOUND)
```

## Root Cause
The issue was caused by a timing problem in the JavaScript module initialization:

1. The `PromptDialog` class was being instantiated immediately when the script loaded
2. In the constructor, it tried to access `window.agentRunUuid` which wasn't set yet
3. The global variables are only set later during DOM initialization
4. This resulted in `this.agentRunUuid` being `undefined`

## Solution Implemented

### 1. Fixed PromptDialog Class (`prompt_dialog.js`)
- **Removed** the assignment of `agentRunUuid` from the constructor
- **Added** a dynamic getter method `getAgentRunUuid()` that accesses `window.agentRunUuid` when needed
- **Added** validation to check if the UUID is available before making API calls
- **Added** better error messages for debugging

### 2. Updated Initialization Pattern
- **Changed** from immediate instantiation to deferred instantiation
- **Added** `initializePromptDialog()` function that creates the instance when needed
- **Modified** global exports to create the instance lazily

### 3. Enhanced Error Handling
- **Added** validation in the `show()` method to check for UUID availability
- **Added** user-friendly error messages when UUID is not available
- **Added** console logging for debugging API calls

### 4. Improved Main Controller Integration
- **Updated** `agent_run_main.js` to properly initialize the prompt dialog after global variables are set
- **Added** logging to track initialization progress

## Changes Made

### `prompt_dialog.js`:
```javascript
// Before:
constructor() {
    this.agentRunUuid = window.agentRunUuid; // This was undefined!
}

// After:
constructor() {
    // No agentRunUuid assignment
}

getAgentRunUuid() {
    return window.agentRunUuid || '';
}
```

### Initialization Pattern:
```javascript
// Before:
const promptDialog = new PromptDialog(); // Immediate instantiation

// After:
let promptDialog = null;
function initializePromptDialog() {
    if (!promptDialog) {
        promptDialog = new PromptDialog();
    }
    return promptDialog;
}
```

### API Call:
```javascript
// Now includes validation:
const agentRunUuid = this.getAgentRunUuid();
if (!agentRunUuid) {
    reject(new Error('Agent run UUID not available'));
    return;
}
```

## Benefits
1. **Fixed the 404 error** - API calls now use the correct UUID
2. **Better error handling** - Clear error messages when things go wrong
3. **Improved debugging** - Console logging to track issues
4. **More robust initialization** - Handles timing issues between modules

## Testing
After implementing these changes:
- The prompt dialog should successfully fetch prompts from the server
- The API URL should contain the correct agent run UUID
- Error messages should be more helpful for debugging

The fix maintains backward compatibility while solving the core timing issue that was causing the undefined UUID problem.
