# Multi-AI Chat System Usage Guide
 
## Getting Started
 
1. **Installation**
   - Clone the repository 
   - Copy `backend/env.example` to `backend/.env` and fill in your API keys
   - Copy `frontend/env.example` to `frontend/.env` and configure API URL
   - Run `./scripts/install.sh` to install dependencies
   - Run `./scripts/start.sh` to start the application
 
2. **Accessing the System**
   - Open `http://localhost` in your browser
   - The backend API is available at `http://localhost:5000/api`
 
## Features 
 
### Chat Sessions
- Create new chat sessions or join existing ones
- Multiple users can participate in the same session 
- Switch between different AI services per session
 
### AI Services 
- **阶跃星辰AI**: Advanced conversational AI with customizable personalities
- **DeepSeek**: Powerful for long-form text generation 
- **MiniChat**: Specialized in voice interactions and voice profiles
- **Minimax**: High-performance conversational AI with group management
- **StepChat**: Fast and efficient chat AI service 
 
### Voice Features 
- Record and send voice messages
- Convert AI responses to speech 
- Customize voice characteristics (pitch, speed)
 
## Customization
 
### Personality Settings (阶跃星辰AI)
- Adjust temperature for more creative/conservative responses
- Select personality traits (friendly, professional, humorous, etc.)
 
### Voice Settings (MiniChat)
- Choose from different voice profiles 
- Adjust pitch and speaking rate 
- Toggle voice response on/off 
 
## Troubleshooting 
 
1. **No Audio**
   - Make sure your browser has microphone permissions 
   - Check that the Google TTS credentials are properly configured
 
2. **AI Not Responding**
   - Verify your API keys are correct in the `.env` file 
   - Check the backend logs for errors 
 
3. **Connection Issues**
   - Ensure all services are running (`ps aux | grep python`, `ps aux | grep nginx`)
   - Check the nginx logs for connection errors
   - Verify database connection: `psql -h 81.70.190.70 -U postgres -d aichat`