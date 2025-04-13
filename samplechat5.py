#Remove UI: Switching to a pure terminal interface for simple understanding and debugging
#Friendlier Responses: from hardcoded questions to more natural, context-aware replies
#Using a lightweight approach to generate responses dynamically based on user input
#Code Efficiency: Optimize loops, reduced redundant operations and improved resource 

from textblob import TextBlob
import json
import os
from datetime import datetime
import random
from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import time  # Added missing import

# Initialize pyttsx3 for offline TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Faster speech

# Load or create user profile
def load_profile():
    if os.path.exists("user_profile.json"):
        with open("user_profile.json", "r") as file:
            return json.load(file)
    return {
        "user_name": "",
        "chatbot_name": "",
        "interests": [],
        "struggles": [],
        "relationships": {},
        "goals": [],
        "last_suggestion": ""
    }

# Save user profile
def save_profile(profile):
    with open("user_profile.json", "w") as file:
        json.dump(profile, file, indent=4)

# Analyze emotion
def analyze_emotion(text):
    analysis = TextBlob(text)
    text_lower = text.lower()
    if any(word in text_lower for word in ["not", "bad", "low", "heavy", "demot"]) or analysis.sentiment.polarity < 0:
        return "negative"
    elif any(word in text_lower for word in ["enjoy", "good", "great"]) or analysis.sentiment.polarity > 0:
        return "positive"
    return "neutral"

# Dynamic suggestions
def make_suggestion(profile, emotion, user_input):
    base_phrases = {
        "positive": ["That’s awesome!", "Love that vibe!", "Sweet!"],
        "negative": ["Ouch, that’s tough.", "I feel you.", "Rough one, huh?"],
        "neutral": ["Cool, what’s up?", "Oh, nice!", "Alrighty then!"]
    }
    follow_ups = []
    if profile["interests"] and random.choice([True, False]):
        interest = random.choice(profile["interests"])
        follow_ups.extend([f"Anything to do with {interest}?", f"Been into {interest} lately?"])
    elif profile["relationships"] and random.choice([True, False]):
        person = random.choice(list(profile["relationships"].keys()))
        relation = profile["relationships"][person]["relation_type"]
        follow_ups.extend([f"How’s your {relation} {person} taking it?", f"Chatted with {person} about this?"])
    else:
        follow_ups.extend(["What’s on your mind?", "How’s that going for you?"])
    
    base = random.choice(base_phrases[emotion])
    follow = random.choice(follow_ups)
    return f"{base} {follow}".strip()

# Log conversation
def log_conversation(diary_file, user_input, bot_response):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    with open(diary_file, "a") as file:
        file.write(f"[{time_str}] Me: {user_input}\n")
        file.write(f"[{time_str}] {profile['chatbot_name']}: {bot_response}\n")

# Analyze conversation for diary
def analyze_conversation(conversation_log):
    emotions, entry_parts, intentions = set(), [], set()
    for user_input, _ in conversation_log:
        emotion = analyze_emotion(user_input)
        if emotion != "neutral":
            emotions.add(f"felt {emotion.replace('positive', 'good').replace('negative', 'low')}")
        user_lower = user_input.lower()
        if "feel" in user_lower:
            entry_parts.append(user_input) if user_input not in entry_parts else None
        elif "friend" in user_lower or "relationship" in user_lower:
            words = user_lower.split()
            try:
                relation_type = "friend" if "friend" in words else "relationship"
                name = words[words.index(relation_type) + 1]
                issue = " ".join(words[words.index(relation_type) + 2:]) or "mentioned"
                rel_str = f"about my {relation_type} {name} ({issue})"
                entry_parts.append(rel_str) if rel_str not in entry_parts else None
            except:
                entry_parts.append(user_input) if user_input not in entry_parts else None
        elif "like" in user_lower or "enjoy" in user_lower:
            words = user_lower.split()
            try:
                keyword = next(word for word in ["like", "enjoy"] if word in user_lower)
                thing = " ".join(words[words.index(keyword) + 1:words.index(keyword) + 3]) if words.index(keyword) + 2 < len(words) else words[words.index(keyword) + 1]
                if thing not in ["to", "the", "a", "and"]:
                    entry_parts.append(f"enjoyed {thing}") if f"enjoyed {thing}" not in entry_parts else None
            except:
                entry_parts.append(user_input) if user_input not in entry_parts else None
        elif "want" in user_lower:
            intent = user_input.split("want", 1)[-1].strip()
            intentions.add(intent)
    
    if not any([emotions, entry_parts, intentions]):
        return f"Not much to say today—just chatted with {profile['chatbot_name']}."
    entry = []
    if emotions:
        entry.append(f"I {' and '.join(sorted(emotions))} today")
    if entry_parts:
        entry.append(", ".join(entry_parts))
    if intentions:
        entry.append(f"and wanted to {' and '.join(sorted(intentions))}")
    return ". ".join([e.strip() for e in entry if e.strip()]) + "."

# Write diary entry
def write_diary_entry(diary_file, conversation_log):
    now = datetime.now()
    date, day = now.strftime("%Y-%m-%d"), now.strftime("%A")
    summary = analyze_conversation(conversation_log)
    with open(diary_file, "a") as file:  # Fixed syntax error
        file.write(f"\n=== Diary Entry for {date} ({day}) ===\n{summary}\n====================\n\n")

# Speak sequentially
def speak(text, chatbot_name):
    engine.say(f"{chatbot_name}: {text}")
    engine.runAndWait()

# Voice input with Vosk
def get_voice_input():
    model_path = "model/vosk-model-small-en-in-0.4"
    if not os.path.exists(model_path):
        print("[Error: Vosk model not found. Download from https://alphacephei.com/vosk/models]")
        return None
    
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("[Listening... Speak now!]")
    try:
        start_time = time.time()
        while time.time() - start_time < 5:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return text
            time.sleep(0.05)
    except Exception as e:
        print(f"[Error: {str(e)}]")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    return None

# Main chat logic
def chat():
    global profile
    profile = load_profile()
    conversation_log = []
    diary_file = "digital_diary.txt"

    # Initial setup
    if not profile["user_name"]:
        print("Hey! I’m your chat buddy. What’s your name?")
        speak("Hey! I’m your chat buddy. What’s your name?", "Bot")
        while not profile["user_name"]:
            user_input = get_voice_input() or input("> ").strip()
            if user_input:
                profile["user_name"] = user_input
                save_profile(profile)
    if not profile["chatbot_name"]:
        print(f"Hi {profile['user_name']}! What should I call myself?")
        speak(f"Hi {profile['user_name']}! What should I call myself?", "Bot")
        while not profile["chatbot_name"]:
            user_input = get_voice_input() or input("> ").strip()
            if user_input:
                profile["chatbot_name"] = user_input
                save_profile(profile)

    # Start chat
    now = datetime.now()
    date, day = now.strftime("%Y-%m-%d"), now.strftime("%A")
    with open(diary_file, "a") as file:
        file.write(f"\n[{date} - {day}]\n")
    
    greeting = f"Hey {profile['user_name']}! It’s {profile['chatbot_name']} here. How’s your day been?"
    print(f"{profile['chatbot_name']}: {greeting}")
    speak(greeting, profile["chatbot_name"])

    while True:
        user_input = get_voice_input()
        if not user_input:
            print("[No voice detected. Type instead?]")
            user_input = input("> ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["bye", "goodbye", "see you"]:
            farewell = f"Take care, {profile['user_name']}! Catch you later!"
            print(f"{profile['chatbot_name']}: {farewell}")
            speak(farewell, profile["chatbot_name"])
            log_conversation(diary_file, user_input, farewell)
            conversation_log.append((user_input, farewell))
            write_diary_entry(diary_file, conversation_log)
            save_profile(profile)
            break
        
        print(f"Me: {user_input}")
        emotion = analyze_emotion(user_input)
        user_lower = user_input.lower()

        # Update profile
        if "like" in user_lower or "enjoy" in user_lower:
            words = user_lower.split()
            try:
                keyword = next(word for word in ["like", "enjoy"] if word in user_lower)
                thing = " ".join(words[words.index(keyword) + 1:words.index(keyword) + 3]) if words.index(keyword) + 2 < len(words) else words[words.index(keyword) + 1]
                if thing not in profile["interests"] and thing not in ["to", "the", "a", "and"]:
                    profile["interests"].append(thing)
            except:
                pass
        elif "struggle" in user_lower or "hard" in user_lower:
            thing = user_input.split("struggle" if "struggle" in user_lower else "hard")[-1].strip()
            if thing and thing not in profile["struggles"]:
                profile["struggles"].append(thing)
        elif "friend" in user_lower or "relationship" in user_lower:
            words = user_lower.split()
            try:
                relation_type = "friend" if "friend" in words else "relationship"
                name = words[words.index(relation_type) + 1]
                if name not in profile["relationships"]:
                    profile["relationships"][name] = {"relation_type": relation_type, "issues": []}
            except:
                pass

        # Generate response
        if "feel" in user_lower:
            response = f"Whoa, sounds {emotion}. What’s stirring that up?"
        elif "day" in user_lower:
            response = f"Your day’s been {emotion}, huh? Spill the tea!"
        elif "friend" in user_lower or "relationship" in user_lower:
            response = f"Friends, huh? What’s the deal there? {make_suggestion(profile, emotion, user_input)}"
        elif emotion == "positive":
            response = f"That’s rad! {make_suggestion(profile, emotion, user_input)}"
        elif emotion == "negative":
            response = f"Bummer, dude. {make_suggestion(profile, emotion, user_input)}"
        else:
            response = f"Neat! {make_suggestion(profile, emotion, user_input)}"

        print(f"{profile['chatbot_name']}: {response}")
        speak(response, profile["chatbot_name"])
        log_conversation(diary_file, user_input, response)
        conversation_log.append((user_input, response))

if __name__ == "__main__":
    profile = None
    chat()