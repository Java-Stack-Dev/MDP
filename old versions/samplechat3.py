#Mood based:Positive emotions get upbeat suggestions, and negative ones get supportive ideas
#Interest based: Ties suggestions to your interests (eg., "music")
#Relationship based: Offers ideas about people you’ve mentioned (eg., Teja)
#Adding speach to text (user input) by google stt api and text to speech (bot output) by pyttsx3 for chat via voice

from textblob import TextBlob
import json
import os
from datetime import datetime
import random
import speech_recognition as sr
from gtts import gTTS
import pygame.mixer
import time

# Initialize pygame mixer
pygame.mixer.init()

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

# Analyze emotion with better detection
def analyze_emotion(text):
    analysis = TextBlob(text)
    text_lower = text.lower()
    if "not" in text_lower or "bad" in text_lower or "low" in text_lower or "heavy" in text_lower or analysis.sentiment.polarity < 0:
        return "negative"
    elif "enjoy" in text_lower or "good" in text_lower or "great" in text_lower or analysis.sentiment.polarity > 0:
        return "positive"
    else:
        return "neutral"

# Suggest something based on profile and mood
def make_suggestion(profile, emotion):
    suggestions = []
    if profile["interests"]:
        interest = profile["interests"][-1]
        if emotion == "positive":
            suggestions.extend([f"How about finding a new {interest} playlist?", f"Ever tried sharing your {interest} with someone?"])
        elif emotion == "negative":
            suggestions.extend([f"Maybe some {interest} could lift your spirits?", f"How about losing yourself in {interest} for a bit?"])
        else:
            suggestions.extend([f"Since you’re into {interest}, maybe give it some time today?", f"Got any {interest} plans coming up?"])
    if profile["relationships"]:
        person = random.choice(list(profile["relationships"].keys()))
        relation_type = profile["relationships"][person]["relation_type"]
        if emotion == "positive":
            suggestions.append(f"Could be fun to hang with your {relation_type} {person}!")
        elif emotion == "negative":
            suggestions.extend([f"Want to talk it out with your {relation_type} {person}?", f"Maybe a small gesture to your {relation_type} {person}?"])
        else:
            suggestions.extend([f"Any plans with your {relation_type} {person} soon?", f"How’s your {relation_type} {person} doing these days?"])
    if not suggestions:
        if emotion == "positive":
            suggestions.append("How about something fun to keep the vibe going?")
        elif emotion == "negative":
            suggestions.append("Maybe a quick break could help?")
        else:
            suggestions.append("How about trying something new today?")
    available = [s for s in suggestions if s != profile.get("last_suggestion", "")]
    if not available:
        available = suggestions
    suggestion = random.choice(available)
    profile["last_suggestion"] = suggestion
    return suggestion

# Log conversation in real-time
def log_conversation(diary_file, user_input, bot_response):
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    with open(diary_file, "a") as file:
        file.write(f"[{time_str}] Me: {user_input}\n")
        file.write(f"[{time_str}] {profile['chatbot_name']}: {bot_response}\n")

# Analyze conversation for diary entry
def analyze_conversation(conversation_log):
    entry_parts = []
    emotions = []
    intentions = []
    for user_input, bot_response in conversation_log:
        emotion = analyze_emotion(user_input)
        if emotion != "neutral":
            emotions.append(f"felt {emotion.replace('positive', 'good').replace('negative', 'low')}")
        
        user_lower = user_input.lower()
        if "feel" in user_lower or "felt" in user_lower:
            entry_parts.append(user_input)
        elif "friend" in user_lower or "relationship" in user_lower:
            words = user_lower.split()
            try:
                relation_type = "friend" if "friend" in words else "relationship"
                name_idx = words.index(relation_type) + 1
                name = words[name_idx]
                issue = " ".join(words[name_idx + 1:]) if name_idx + 1 < len(words) else "mentioned"
                entry_parts.append(f"about my {relation_type} {name} ({issue})")
            except:
                entry_parts.append(user_input)
        elif "like" in user_lower or "enjoy" in user_lower:
            words = user_lower.split()
            try:
                keyword = next(word for word in ["like", "enjoy"] if word in user_lower)
                thing_idx = words.index(keyword) + 1
                thing = " ".join(words[thing_idx:thing_idx + 2]) if thing_idx + 1 < len(words) else words[thing_idx]
                if thing not in ["to", "the", "a", "and"]:
                    entry_parts.append(f"enjoyed {thing}")
            except:
                entry_parts.append(user_input)
        elif "want" in user_lower or "wanted" in user_lower:
            intentions.append(user_input.split("want", 1)[-1].strip())

    if not entry_parts and not emotions and not intentions:
        return "Not much to say today—just chatted with Issabela."
    
    entry = []
    if emotions:
        entry.append(f"I {' and '.join(emotions)} today")
    if entry_parts:
        entry.append(" and ".join(entry_parts))
    if intentions:
        entry.append(f" and wanted {' and '.join(intentions)}")
    
    return ". ".join([e.strip() for e in entry if e.strip()]) + "."

# Write full diary entry at session end
def write_diary_entry(diary_file, conversation_log):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    day = now.strftime("%A")
    summary = analyze_conversation(conversation_log)
    with open(diary_file, "a") as file:
        file.write(f"\n=== Diary Entry for {date} ({day}) ===\n")
        file.write(f"{summary}\n")
        file.write("====================\n\n")

# Convert text to speech and play it
def speak(text, chatbot_name):
    tts = gTTS(text=f"{chatbot_name} says: {text}", lang="en")
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)
    time.sleep(0.5)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(temp_file)

# Get voice input from user
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (say something or type instead)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You (voice): {text}")
            return text
        except sr.WaitTimeoutError:
            print("No voice input detected, please type instead.")
            return None
        except sr.UnknownValueError:
            print("Couldn’t understand that, please try again or type.")
            return None

# Chat with personal touch, memory, and voice
def chat():
    global profile  # Make profile accessible in log_conversation
    profile = load_profile()
    last_mentioned_friend = None
    conversation_log = []

    if not profile["user_name"]:
        print("Hi! I’m your companion. What’s your name?")
        profile["user_name"] = input("You: ").strip()
        save_profile(profile)

    if not profile["chatbot_name"]:
        print(f"Hi {profile['user_name']}! What would you like to call me?")
        profile["chatbot_name"] = input("You: ").strip()
        save_profile(profile)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    day = now.strftime("%A")
    diary_file = "digital_diary.txt"
    with open(diary_file, "a") as file:
        file.write(f"\n[{date} - {day}]\n")
    
    greeting = f"Hi {profile['user_name']}! I’m {profile['chatbot_name']}, here to listen and help. How’s your day going?"
    print(greeting)
    speak(greeting, profile["chatbot_name"])
    
    while True:
        user_input = get_voice_input()
        if not user_input:
            user_input = input("You (type): ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["bye", "goodbye", "see you"]:
            farewell = f"Alright, take care! I’m {profile['chatbot_name']}—always here if you need me."
            print(farewell)
            speak(farewell, profile["chatbot_name"])
            log_conversation(diary_file, user_input, farewell)
            conversation_log.append((user_input, farewell))
            write_diary_entry(diary_file, conversation_log)
            save_profile(profile)
            break
        
        emotion = analyze_emotion(user_input)

        if user_input.lower() in ["thats it", "that’s it", "enough", "done", "thatsall"]:
            if profile["relationships"]:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                response = f"Okay, I’ve got that about your {relation_type} {first_person}. {make_suggestion(profile, emotion)}"
            elif profile["interests"]:
                response = f"Alright, we’ve talked about {profile['interests'][-1]}. {make_suggestion(profile, emotion)}"
            else:
                response = f"Got it. I’m {profile['chatbot_name']}—here whenever you’re ready to chat more. {make_suggestion(profile, emotion)}"
            print(response)
            speak(response, profile["chatbot_name"])
            log_conversation(diary_file, user_input, response)
            conversation_log.append((user_input, response))
            save_profile(profile)
            continue

        if user_input.lower() in ["nahh", "nope", "no", "nvm", "nah"]:
            response = f"Okay, great! I’m {profile['chatbot_name']}—let me know if you need any assistance or just want to chat later. {make_suggestion(profile, emotion)}"
            print(response)
            speak(response, profile["chatbot_name"])
            log_conversation(diary_file, user_input, response)
            conversation_log.append((user_input, response))
            save_profile(profile)
            continue

        if "like" in user_input.lower() or "interest" in user_input.lower() or "enjoy" in user_input.lower():
            words = user_input.lower().split()
            try:
                keyword = next(word for word in ["like", "interest", "enjoy"] if word in user_input.lower())
                thing_idx = words.index(keyword) + 1
                thing = " ".join(words[thing_idx:thing_idx + 2]) if thing_idx + 1 < len(words) else words[thing_idx]
                if thing in ["to", "the", "a", "and"]:
                    thing = words[thing_idx + 1] if thing_idx + 1 < len(words) else thing
                if thing not in profile["interests"]:
                    profile["interests"].append(thing)
                    save_profile(profile)
                response = f"Got it, you’re into {thing}! What do you love most about it?" if emotion == "positive" else f"Got it, you enjoy {thing}. What’s that been like for you today?"
                print(response)
                speak(response, profile["chatbot_name"])
            except:
                response = "I caught that you enjoy something—what is it you’re into?"
                print(response)
                speak(response, profile["chatbot_name"])
        
        elif "struggle" in user_input.lower() or "hard" in user_input.lower():
            thing = user_input.split("struggle" if "struggle" in user_input.lower() else "hard")[-1].strip()
            if thing not in profile["struggles"]:
                profile["struggles"].append(thing)
                save_profile(profile)
            response = f"That sounds tough—{thing} is no joke. How can I support you with it?"
            print(response)
            speak(response, profile["chatbot_name"])
        
        elif "friend" in user_input.lower() or "relationship" in user_input.lower():
            words = user_input.lower().split()
            try:
                relation_type = "friend" if "friend" in words else "relationship"
                name_idx = words.index(relation_type) + 1
                name = words[name_idx]
                issue = " ".join(words[name_idx + 1:]) if name_idx + 1 < len(words) else "mentioned"
                if name not in profile["relationships"]:
                    profile["relationships"][name] = {"relation_type": relation_type, "issues": []}
                if issue not in profile["relationships"][name]["issues"]:
                    profile["relationships"][name]["issues"].append(issue)
                    save_profile(profile)
                if name != last_mentioned_friend:
                    response = f"Got it, something’s up with your {relation_type} {name}. What happened there?"
                    last_mentioned_friend = name
                else:
                    response = f"More about your {relation_type} {name}—how does that make you feel?"
                print(response)
                speak(response, profile["chatbot_name"])
            except:
                response = "Tell me more about this friend or relationship—what’s going on?"
                print(response)
                speak(response, profile["chatbot_name"])
        
        elif emotion == "positive":
            response = f"Love that you’re feeling good! Is it tied to {profile['interests'][-1]} or something new?" if profile["interests"] else "Nice to hear you’re doing well! What’s sparking that joy?"
            print(response)
            speak(response, profile["chatbot_name"])
        
        elif emotion == "negative":
            if "sob" in user_input.lower() or "cry" in user_input.lower() or "heavy" in user_input.lower():
                response = f"I’m so sorry you’re feeling that heavy—I can hear how much it’s weighing on you. Want to let it out?"
                if "feeling heavy" not in profile["struggles"]:
                    profile["struggles"].append("feeling heavy")
                    save_profile(profile)
            elif "yes" in user_input.lower() or "sure" in user_input.lower():
                response = "I’m all ears—go ahead and tell me what’s been on your chest."
            elif profile["relationships"]:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                response = f"I’m sorry you’re down. Is this about your {relation_type} {first_person} or something else weighing on you?"
            elif profile["struggles"]:
                response = f"I feel you—could this be tied to {profile['struggles'][0]}? Want to talk it out?"
            else:
                response = "I’m here for you. What’s got you feeling this way?"
            print(response)
            speak(response, profile["chatbot_name"])
        
        else:
            if "day" in user_input.lower():
                response = f"More about your day—did {profile['interests'][-1]} play a part?" if profile["interests"] else "Tell me more about how it’s been going!"
            elif "feel" in user_input.lower():
                response = f"Feelings can be heavy—any chance it’s linked to {profile['struggles'][0]}?" if profile["struggles"] else "I’m listening—how are you holding up?"
            elif "silent" in user_input.lower() or "alone" in user_input.lower():
                response = f"I get that silence—I’ve been there too. What’s it like for you right now? {make_suggestion(profile, emotion)}"
            elif "?" in user_input:
                if "should" in user_input.lower() and profile["relationships"]:
                    first_person = list(profile["relationships"].keys())[0]
                    relation_type = profile["relationships"][first_person]["relation_type"]
                    response = f"Hmm, asking your {relation_type} {first_person} could clear things up. What do you think might happen if you do?"
                else:
                    response = "That’s a good question! What do you feel like doing about it?"
            elif "friend" in user_input.lower() and profile["relationships"]:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                response = f"About your {relation_type} {first_person}—how do you usually handle stuff like this with him?"
            else:
                response = f"I’m here. What else is on your heart? {make_suggestion(profile, emotion)}"
            print(response)
            speak(response, profile["chatbot_name"])
        
        log_conversation(diary_file, user_input, response)
        conversation_log.append((user_input, response))
        
        if "silent" in user_input.lower() or "alone" in user_input.lower():
            response = f"You don’t have to carry it alone—I’ve felt that quiet weight too. Want to let some of it out? {make_suggestion(profile, emotion)}"
            print(response)
            speak(response, profile["chatbot_name"])
            log_conversation(diary_file, user_input, response)
            conversation_log.append((user_input, response))
        elif "friend" in user_input.lower() and profile["relationships"]:
            first_person = random.choice(list(profile["relationships"].keys()))
            relation_type = profile["relationships"][first_person]["relation_type"]
            response = f"Speaking of your {relation_type}, how’s things with {first_person} lately? {make_suggestion(profile, emotion)}"
            print(response)
            speak(response, profile["chatbot_name"])
            log_conversation(diary_file, user_input, response)
            conversation_log.append((user_input, response))

chat()