# Voice Calling Setup Guide

## Overview
The VoiceRAG application now includes phone calling functionality! You can call a phone number and have the AI assistant answer questions about your documents using voice.

## Features
- **Outbound Calling**: Call any phone number and connect to the AI assistant
- **Voice AI**: The AI responds using natural voice synthesis
- **RAG Integration**: Answers are based on your uploaded documents
- **Real-time Conversation**: Natural back-and-forth voice conversation

## Setup Instructions

### 1. Get Twilio Credentials

1. Sign up for a [Twilio account](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number from Twilio
4. Note down your credentials:
   - Account SID
   - Auth Token
   - Phone Number (e.g., +1234567890)

### 2. Configure Environment Variables

Update your `app/backend/.env` file with your Twilio credentials:

```bash
# Twilio Configuration for Calling Feature
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### 3. Install Dependencies

The required packages have been added to `requirements.txt`. If you're running in a virtual environment, install them:

```bash
pip install twilio azure-communication-callautomation
```

### 4. Restart the Application

Restart both the backend and frontend servers to load the new configuration:

```bash
# Backend (in one terminal)
cd app/backend
python app.py

# Frontend (in another terminal)
cd app/frontend
npm run dev
```

## How to Use

1. Open your browser and go to `http://localhost:5173`
2. Log in to your account
3. Click the **"Call"** button in the navigation
4. Enter a phone number (e.g., +1 (555) 123-4567)
5. Click **"Call AI Assistant"**
6. The AI will call the number and start a voice conversation
7. Ask questions about your documents - the AI will search and respond with voice

## API Endpoints

The calling feature adds these new API endpoints:

- `POST /call/initiate` - Start a new call
- `GET /call/status/{call_sid}` - Get call status
- `POST /call/end/{call_sid}` - End a call
- `POST /call/twiml` - Handle Twilio webhooks (internal)

## Troubleshooting

### Common Issues:

1. **"Invalid phone number"**: Make sure the number includes country code (e.g., +1 for US)

2. **"Twilio authentication failed"**: Check your Account SID and Auth Token in .env

3. **"Call failed"**: Ensure your Twilio account has sufficient balance and the number is valid

4. **"AI not responding"**: Check that your Azure OpenAI and Search credentials are configured

### Testing:

1. Test with your own phone number first
2. Check the backend logs for any errors
3. Verify Twilio webhook URLs are accessible (the app handles this automatically)

## Security Notes

- Phone numbers are validated before calling
- All calls are logged for monitoring
- JWT authentication is required for API access
- Twilio credentials are stored securely in environment variables

## Cost Information

- Twilio charges per minute for calls
- Azure OpenAI charges for voice synthesis
- Check Twilio and Azure pricing for your region

## Next Steps

1. Test the calling feature with your documents
2. Customize the AI's voice and personality in the code
3. Add call recording functionality if needed
4. Integrate with your existing phone systems

The calling feature is now ready to use! 🎉
