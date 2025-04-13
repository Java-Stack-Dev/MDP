# Empathetic Multilingual AI Assistant

This is a voice-enabled, emotionally intelligent AI assistant designed to provide mental and emotional support, manage daily tasks, and maintain a personal digital diary. Inspired by the vision of a supportive companion like JARVIS from Iron Man, the assistant adapts to your chosen name (e.g., "Issabela" or anything you like), listens, responds with empathy, and assists in English, Telugu, and Hindi. Built with moral values at its core, it aims to uplift users, help them express their feelings, and stay organized—all while maintaining a warm, human-like interaction.

Developed by Sai Tarun, this project combines speech recognition, text-to-speech, and rule-based natural language processing to create a meaningful tool for those seeking a friend-like assistant.

## Table of Contents
- [Features](#features)
- [Motivation](#motivation)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Features

The assistant is packed with features to support and organize your life:

Voice Interaction:
  - Speech-to-Text (STT): Uses `speech_recognition` with Google’s free API to transcribe user speech in real-time.
  - Text-to-Speech (TTS): Employs `gTTS` for natural-sounding responses in English (`en`), Telugu (`te`), and Hindi (`hi`).
  - Playback handled via `pygame.mixer` for reliable audio output.

Multilingual Support:
  - Seamlessly switches between English, Telugu, and Hindi based on user commands (e.g., “switch to Telugu language”).
  - Supports culturally relevant responses, with plans to deepen Telugu and Hindi emotional nuance.

Customizable Name:
  - Users choose the assistant’s name on first run (e.g., “Issabela,” “Jarvis,” or anything personal).
  - Persists across sessions via `user_profile.json`.

Emotion Detection:
  - Analyzes user input using `TextBlob` and keyword matching to detect moods (positive, negative, neutral).
  - Responds empathetically, e.g., “I’m sorry you’re feeling down. What’s going on?” for negative inputs like “unhappy.”

Task Management:
  - Sets reminders via voice or text (e.g., “remind me to call mom at 2 PM”).
  - Parses basic time expressions using `dateutil.parser` for scheduling.
  - Alerts users when reminders are due.

Digital Diary:
  - Logs every conversation with timestamp, user input, mood, topic, and assistant’s response.
  - Saves to `digital_diary.txt` for reflection and journaling.
  - Stores user profile (name, assistant name, language, reminders) in `user_profile.json`.

Moral and Supportive Design:
  - Hardcoded to avoid negative or harmful responses, ensuring an uplifting tone.
  - Encourages users to share feelings, offering comfort for inputs like “I’m not okay” or “nenu bagaledu” (Telugu: “I’m not okay”).

## Motivation

This project was born from a desire to create an AI that goes beyond functionality to offer genuine emotional support. Many people struggle to express their feelings or manage daily tasks under stress. The assistant aims to:
- Provide a safe, non-judgmental space for users to voice their thoughts.
- Support multilingual communities, especially in India, with native Telugu and Hindi interactions.
- Empower users with reminders and journaling to stay organized and reflective.
- Uphold moral values by fostering kindness, empathy, and positivity.

The customizable name lets users personalize their companion, making it feel like a true friend tailored to their needs.

## Architecture

The assistant’s architecture is modular and rule-based, prioritizing simplicity and reliability:

Input Processing:
  - STT (`speech_recognition`): Captures voice via microphone, transcribes using Google’s API.
  - Fallback to text input if voice isn’t detected.

Core Logic:
  - Emotion Detection: Combines `TextBlob` sentiment analysis with keyword checks (e.g., “unhappy” → negative).
  - Context Tracking: Maintains `last_topic` (e.g., “conversation,” “food”) to keep responses relevant.
  - Response Generation: Uses rule-based templates for empathy and variety, with multilingual support.

Output:
  - TTS ( gTTS ): Converts responses to audio in the user’s chosen language.
  -  pygame.mixer : Plays audio reliably on Windows and other platforms.

Persistence:
  -  user_profile.json : Stores user name, assistant name, language, reminders, and diary entries.
  -  digital_diary.txt : Logs interactions for journaling.

Dependencies include:
- `speech_recognition` for STT
- `gTTS` for TTS
- `pygame` for audio playback
- `TextBlob` for sentiment analysis
- `python-dateutil` for reminder parsing
- `PyAudio` for microphone input

## Installation

Follow these steps to set up the assistant on your system:

### Prerequisites
- Python 3.7+
- A working microphone
- Internet connection (for STT and TTS APIs)
- Windows, macOS, or Linux

### Steps
1. Clone the Repository (or download the code):
   bash
   git clone <your-repo-url>
   cd empathetic-assistant

2. Install Dependencies:
   bash
   pip install -r requirements.txt
   

   Note: On Windows, if `PyAudio` fails, try:
   bash
   pip install pipwin
   pipwin install pyaudio
   

3. Verify Setup:
   Ensure your microphone is connected and speakers are on.

4. Run the Program:
   bash
   python llmchatbot.py
   

## Usage

1. Start the Chatbot:
   Run `python llmchatbot.py`. The assistant will greet you:
   
   Hey! I’m your friend here to help. What’s your name?
   

2. Set Names:
   - Enter your name (e.g., “Sai”).
   - Choose a name for the assistant (e.g., “Issabela,” “Amigo,” or anything you like).

3. Interact:
   - Voice Input: Speak clearly when prompted (“[Listening... Speak now!]”).
   - Text Input: Type if voice fails (“[No voice detected. Type instead?]”).
     Example commands:
     - “I’m feeling great” → “Awesome vibes! What’s the highlight?”
     - “nenu bagaledu” (Telugu: “I’m not okay”) → “Nīvu bādhapadutunnāvu ani cūsi badha vēstundi. Emi jarigindi?”
     - “remind me to call mom at 2 PM” → “Got it, I’ll remind you to call mom at 14:00!”
     - “switch to Telugu language” → “Switched to Telugu for you!”

4. Exit:
   Say or type “bye” to end:
   
   Take care, <your_name>! I’m here whenever you need me.
   

5. Check Outputs:
   - `user_profile.json`: Stores your preferences, assistant name, and reminders.
   - `digital_diary.txt`: Logs chats, e.g.:
     
     [2025-04-04 02:00] sai: unhappy | Mood: negative | Topic:  | <assistant_name>: I’m sorry you’re feeling down. What’s going on?
     [2025-04-04 02:01] sai: notsleep now | Mood: negative | Topic: sleep | <assistant_name>: Not sleeping well, huh? Maybe a quick rest could help?
     

## File Structure


MDP/
├── .gitignore             # Ignores generated files
├── llmchatbot.py          # Main chatbot script
├── README.md              # Project documentation
├── requirements.txt       # Lists dependencies


Generated Files (not tracked):
- `user_profile.json` - Stores user data (created on first run).
- `digital_diary.txt` - Logs conversations (created during use).
- `output.mp3` - Temporary audio file (deleted after playback).

## Future Enhancements

The assistant’s got big potential! Planned upgrades include:
- Advanced NLP: Integrate a lightweight LLM for more natural responses.
- Offline Mode: Support offline STT/TTS with Vosk or Coqui.
- Deep Multilingualism: Custom Telugu/Hindi emotion models for better cultural fit.
- Smart Reminders: Full calendar integration and recurring tasks.
- Mood Insights: Analyze diary entries for emotional trends.
- UI: Add a simple GUI for non-voice users.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repo.
2. Create a branch (`git checkout -b feature/your-idea`).
3. Commit changes (`git commit -m "Add your idea"`).
4. Push (`git push origin feature/your-idea`).
5. Open a pull request.

Please ensure code aligns with the project’s moral and empathetic goals.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
Built with ❤️ by Sai Tarun. Name your assistant and let it be your friend in tough times and good!
