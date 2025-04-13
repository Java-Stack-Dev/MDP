import speech_recognition as sr
from gtts import gTTS
import pygame.mixer
import json
import os
from datetime import datetime
from textblob import TextBlob
import random
import time

# Initialize pygame mixer
pygame.mixer.init()

# Load or create user profile
def load_profile():
    if os.path.exists("user_profile.json"):
        with open("user_profile.json", "r", encoding='utf-8') as file:
            profile = json.load(file)
            if "language" not in profile:
                profile["language"] = "en"
            if "last_topic" not in profile:
                profile["last_topic"] = ""
            return profile
    return {
        "user_name": "",
        "chatbot_name": "",
        "language": "en",
        "reminders": [],
        "interests": [],
        "diary": [],
        "last_topic": ""
    }

# Save user profile
def save_profile(profile):
    with open("user_profile.json", "w", encoding='utf-8') as file:
        json.dump(profile, file, indent=4)

# Analyze emotion
def analyze_emotion(text):
    analysis = TextBlob(text)
    text_lower = text.lower()
    negative_keywords = ["sad", "low", "bad", "hurt", "sorry", "unhappy", "not", "sleep"]
    positive_keywords = ["good", "great", "happy", "love"]
    if any(word in text_lower for word in negative_keywords):
        return "negative"
    elif any(word in text_lower for word in positive_keywords):
        return "positive"
    return "neutral" if analysis.sentiment.polarity == 0 else "positive" if analysis.sentiment.polarity > 0 else "negative"

# Update topic based on input
def update_topic(user_input, profile):
    text_lower = user_input.lower()
    if "conversation" in text_lower or "talk" in text_lower or "chat" in text_lower:
        return "conversation"
    elif "joke" in text_lower or "jokes" in text_lower:
        return "jokes"
    elif "food" in text_lower or "eat" in text_lower:
        return "food"
    elif "friend" in text_lower or "friends" in text_lower:
        return "friends"
    elif "sleep" in text_lower:
        return "sleep"
    return "" if len(text_lower.split()) < 3 else profile["last_topic"]  # Reset for short inputs

# Generate smarter, context-aware response
def generate_response(user_input, emotion, profile):
    text_lower = user_input.lower()
    profile["last_topic"] = update_topic(user_input, profile)
    
    # Task handling
    if "help" in text_lower:
        return "I’m here for you! What do you need help with today?"
    elif "remind" in text_lower:
        task = text_lower.split("remind me to", 1)[-1].strip() if "remind me to" in text_lower else "do something"
        profile["reminders"].append({"task": task, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
        return f"Got it, I’ll remind you to {task} soon—any specific time you want?"

    # Emotional and contextual responses
    if emotion == "negative":
        if "not" in text_lower or "nothing" in text_lower:
            return "Sounds like something’s bothering you. Want to talk it out?"
        elif "sleep" in text_lower:
            return "Not sleeping well, huh? What’s keeping you up?"
        return random.choice([
            "I’m sorry you’re feeling down. What’s going on?",
            "Rough patch? How can I help you through it?",
            "You’re not alone in this. What’s on your mind?"
        ])
    elif emotion == "positive":
        if profile["last_topic"] == "conversation":
            if "friend" in text_lower or "friends" in text_lower:
                return "Sweet, catching up with friends is gold! What’d you guys talk about?"
            elif any(name in text_lower for name in ["krishna", "teja"]):
                return f"Chatting with {user_input.split()[-1]}, huh? What’s cool about them?"
            return random.choice([
                "Good talks are the best! What made it so great?",
                "Love that vibe! What sparked that convo?"
            ])
        elif profile["last_topic"] == "jokes":
            return random.choice([
                "Jokes are my jam! Got one to share?",
                "Nice, a good laugh goes a long way. What’s your favorite?"
            ])
        elif profile["last_topic"] == "food":
            return random.choice([
                "Oh, food’s the best mood-lifter! What are you eating?",
                "Yum, good food’s a win! What’s on the menu?"
            ])
        return random.choice([
            "That’s fantastic! What’s driving that happiness?",
            "Awesome vibes! What’s the highlight of your day?"
        ])
    else:
        if len(text_lower.split()) < 3:
            return random.choice([
                "Hmm, tell me a bit more—what’s up?",
                "Short and sweet, huh? What’s on your mind?"
            ])
        if "nothing" in text_lower:
            return "All quiet? Want me to suggest something—like a snack or a quick chat?"
        elif profile["last_topic"] == "sleep":
            return "Sleep on your mind? Planning to rest soon?"
        elif profile["last_topic"]:
            return f"Still on {profile['last_topic']}? What’s next for you?"
        return random.choice([
            "What’s brewing in your world today?",
            "Hey, what’s the next thing on your mind?"
        ])

# Log to diary with analysis
def log_diary(profile, user_input, emotion, response):
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user_input": user_input,
        "emotion": emotion,
        "response": response,
        "topic": profile["last_topic"]
    }
    profile["diary"].append(entry)
    with open("digital_diary.txt", "a", encoding='utf-8') as file:  # Fixed: encoding='utf-8'
        file.write(f"[{entry['date']}] {profile['user_name']}: {user_input} | Mood: {emotion} | Topic: {entry['topic']} | {profile['chatbot_name']}: {response}\n")

# Speech-to-Text
def get_voice_input(language="en"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Listening... Speak now!]")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language=language)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[Error: Could not request results; {e}]")
            return None

# Text-to-Speech
def speak_text(text, language="en"):
    tts = gTTS(text=text, lang=language, slow=False)
    filename = "output.mp3"
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(filename)

# Main chat logic
def chat():
    global profile
    profile = load_profile()
    
    if not profile["user_name"]:
        greeting = "Hey! I’m your friend here to help. What’s your name?"
        print(greeting)
        speak_text(greeting, profile["language"])
        while not profile["user_name"]:
            user_input = get_voice_input(profile["language"]) or input("> ").strip()
            if user_input:
                profile["user_name"] = user_input
                save_profile(profile)
    if not profile["chatbot_name"]:
        greeting = f"Hi {profile['user_name']}! What should I call myself?"
        print(greeting)
        speak_text(greeting, profile["language"])
        while not profile["chatbot_name"]:
            user_input = get_voice_input(profile["language"]) or input("> ").strip()
            if user_input:
                profile["chatbot_name"] = user_input
                save_profile(profile)

    greeting = f"Hey {profile['user_name']}! It’s {profile['chatbot_name']} here. How are you feeling today?"
    print(f"{profile['chatbot_name']}: {greeting}")
    speak_text(greeting, profile["language"])

    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for reminder in profile["reminders"][:]:
            if reminder["time"] <= now:
                reminder_text = f"Reminder: Time to {reminder['task']}!"
                print(f"{profile['chatbot_name']}: {reminder_text}")
                speak_text(reminder_text, profile["language"])
                profile["reminders"].remove(reminder)
                save_profile(profile)

        user_input = get_voice_input(profile["language"])
        if not user_input:
            print("[No voice detected. Type instead?]")
            user_input = input("> ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["bye", "goodbye", "see you"]:
            farewell = f"Take care, {profile['user_name']}! I’m here whenever you need me."
            print(f"{profile['chatbot_name']}: {farewell}")
            speak_text(farewell, profile["language"])
            log_diary(profile, user_input, "neutral", farewell)
            save_profile(profile)
            break
        
        if "language" in user_input.lower():
            lang_map = {"telugu": "te", "hindi": "hi", "english": "en"}
            lang = user_input.lower().split("language", 1)[-1].strip()
            if lang in lang_map:
                profile["language"] = lang_map[lang]
                save_profile(profile)
                response = f"Switched to {lang} for you!"
            else:
                response = "I can do English, Telugu, or Hindi for now. Which one?"
            print(f"{profile['chatbot_name']}: {response}")
            speak_text(response, profile["language"])
            continue

        print(f"Me: {user_input}")
        emotion = analyze_emotion(user_input)
        response = generate_response(user_input, emotion, profile)
        print(f"{profile['chatbot_name']}: {response}")
        speak_text(response, profile["language"])
        log_diary(profile, user_input, emotion, response)

if __name__ == "__main__":
    profile = None
    chat()