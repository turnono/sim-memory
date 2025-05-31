# ADK VertexAI Session Service Setup Guide

This guide walks you through setting up and using your `sim_guide` agent with the proper ADK `VertexAiSessionService` for session management.

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with billing enabled
2. **Service Account**: Already configured (`taajirah-agents-service-account.json`)
3. **Required APIs**: Ensure these APIs are enabled in your project:
   - Vertex AI API
   - AI Platform API

## Setup Steps

### 1. Install Dependencies

```bash
make install-adk
```

Or manually:

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Set these environment variables (or add to your shell profile):

```bash
export PROJECT_ID=taajirah
export LOCATION=us-central1

```

### 3. Test the Setup

Run the integration test to verify everything is configured correctly:

```bash
make test-adk
```

This will check:

- ✅ Service account authentication
- ✅ Environment variables
- ✅ ADK imports
- ✅ Agent configuration
- ✅ Session service setup
