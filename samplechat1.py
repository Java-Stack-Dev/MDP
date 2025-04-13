from textblob import TextBlob
import json
import os
from datetime import datetime

# Load or create user profile
def load_profile():
    if os.path.exists("user_profile.json"):
        with open("user_profile.json", "r") as file:
            return json.load(file)
    return {"likes": [], "struggles": [], "goals": [], "name": ""}

# Save user profile
def save_profile(profile):
    with open("user_profile.json", "w") as file:
        json.dump(profile, file)

# Analyze emotion
def analyze_emotion(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"

# Save journal entry with time only
def save_journal(entry, diary_file):
    now = datetime.now()
    time = now.strftime("%H:%M:%S")  # e.g., 14:30:45
    with open(diary_file, "a") as file:
        file.write(f"[{time}] {entry}\n")

# Chat with personal touch
def chat():
    profile = load_profile()
    if not profile["name"]:
        print("Hey! I’m your companion. What’s your name?")
        profile["name"] = input("You: ")
        save_profile(profile)

    # Set up diary with date at the top
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")  # e.g., 2025-04-02
    day = now.strftime("%A")         # e.g., Wednesday
    diary_file = "digital_diary.txt"
    with open(diary_file, "a") as file:
        file.write(f"\n[{date} - {day}]\n")
    
    print(f"Hi {profile['name']}! I’m here to listen and help. How’s your day going?")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["bye", "that’s all", "enough", "goodbye", "see you"]:
            print("Alright, take care! I’m always here if you need me.")
            break
        
        # Analyze emotion and save journal
        emotion = analyze_emotion(user_input)
        save_journal(user_input, diary_file)

        # Learn about the user
        if "like" in user_input.lower():
            thing = user_input.split("like")[-1].strip()
            profile["likes"].append(thing)
            save_profile(profile)
            print(f"Got it, you like {thing}! What do you enjoy most about it?")
        elif "struggle" in user_input.lower() or "hard" in user_input.lower():
            thing = user_input.split("struggle" if "struggle" in user_input.lower() else "hard")[-1].strip()
            profile["struggles"].append(thing)
            save_profile(profile)
            print(f"That sounds rough—{thing} can be a lot. How can I help you with it?")
        
        # Contextual responses based on emotion and content
        elif emotion == "positive":
            if profile["likes"]:
                print(f"Love hearing you’re in a good mood! Is it something like {profile['likes'][0]} making your day?")
            else:
                print("Nice to hear you’re doing well! What’s got you feeling so good?")
        elif emotion == "negative":
            print("I’m really sorry you’re feeling that way. Want to tell me more about what’s going on?")
        else:
            # Avoid repetition by checking the input
            if "day" in user_input.lower():
                print("Tell me more about how it’s been going!")
            elif "feel" in user_input.lower():
                print("I’m listening—how are you holding up?")
            elif "silent" in user_input.lower() or "alone" in user_input.lower():
                print("I get that—I’ve felt that quiet weight too. What’s it like for you right now?")
            else:
                print("I’m here. What else is on your heart?")  # Less repetitive fallback
        
        # Personal nudge for specific cases
        if "silent" in user_input.lower() or "alone" in user_input.lower():
            print("You don’t have to carry it alone here—I’ve had those moments too. Want to let some of it out?")

chat()