#The profile now uses "user_name" and "chatbot_name" instead of just name 
#You can now pick the chatbot’s name (e.g., Issabela) as per users choice
#It catches interests from “like,” “interest,” or “enjoy” (e.g., “music” from “enjoying the music”)
#Relationships now show the type (e.g., “friend Teja”) and relationships include a "relation_type" like "friend" ,"father"
#Saying “thats it” pauses with context, “nahh” winds down politely 
#Responses now use what it knows (e.g., “Is this about your friend Teja?”)



from textblob import TextBlob
import json
import os
from datetime import datetime

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
        "goals": []
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

# Save journal entry with time only
def save_journal(entry, diary_file):
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    with open(diary_file, "a") as file:
        file.write(f"[{time}] {entry}\n")

# Chat with personal touch and memory
def chat():
    profile = load_profile()
    last_mentioned_friend = None

    if not profile["user_name"]:
        print("Hi! I’m your companion. What’s your name?")
        profile["user_name"] = input("You: ").strip()
        save_profile(profile)

    if not profile["chatbot_name"]:
        print(f"Hi {profile['user_name']}! What would you like to call me?")
        profile["chatbot_name"] = input("You: ").strip()
        save_profile(profile)

    # Set up diary with date at the top
    now = datetime.now()
    date = now.strftime("%Y-%m-d")
    day = now.strftime("%A")
    diary_file = "digital_diary.txt"
    with open(diary_file, "a") as file:
        file.write(f"\n[{date} - {day}]\n")
    
    print(f"Hi {profile['user_name']}! I’m {profile['chatbot_name']}, here to listen and help. How’s your day going?")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["bye", "goodbye", "see you", "chat later", "exit"]:
            print(f"Alright, take care! I’m {profile['chatbot_name']}—always here if you need me.")
            break
        
        # Analyze emotion and save journal
        emotion = analyze_emotion(user_input)
        save_journal(user_input, diary_file)

        # Handle "that's it" or similar as a pause
        if user_input.lower() in ["thats it", "that’s it", "enough", "done", "thatsall"]:
            if profile["relationships"] and len(profile["relationships"]) > 0:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                print(f"Okay, I’ve got that about your {relation_type} {first_person}. Anything else you want to figure out about it?")
            elif profile["interests"]:
                print(f"Alright, we’ve talked about {profile['interests'][0]}. Want to dive deeper into that?")
            else:
                print(f"Got it. I’m {profile['chatbot_name']}—here whenever you’re ready to chat more.")
            continue

        # Handle "nahh," "nope," etc. to wind down
        if user_input.lower() in ["nahh", "nope", "no", "nvm", "nah"]:
            print(f"Okay, great! I’m {profile['chatbot_name']}—let me know if you need any assistance or just want to chat later.")
            continue

        # Learn about the user - improved interest detection
        if "like" in user_input.lower() or "interest" in user_input.lower() or "enjoy" in user_input.lower():
            words = user_input.lower().split()
            try:
                keyword = next(word for word in ["like", "interest", "enjoy"] if word in user_input.lower())
                thing_idx = words.index(keyword) + 1
                thing = words[thing_idx]
                if thing_idx + 1 < len(words) and words[thing_idx + 1] not in ["and", "but", "when", "because"]:
                    thing += " " + words[thing_idx + 1]
                if thing not in profile["interests"]:
                    profile["interests"].append(thing)
                    save_profile(profile)
                if emotion == "positive":
                    print(f"Got it, you’re into {thing}! What do you love most about it?")
                else:
                    print(f"Got it, you enjoy {thing}. What’s that been like for you today?")
            except:
                print("I caught that you enjoy something—what is it you’re into?")
        
        elif "struggle" in user_input.lower() or "hard" in user_input.lower():
            thing = user_input.split("struggle" if "struggle" in user_input.lower() else "hard")[-1].strip()
            if thing not in profile["struggles"]:
                profile["struggles"].append(thing)
                save_profile(profile)
            print(f"That sounds tough—{thing} is no joke. How can I support you with it?")
        
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
                    print(f"Got it, something’s up with your {relation_type} {name}. What happened there?")
                    last_mentioned_friend = name
                else:
                    print(f"More about your {relation_type} {name}—how does that make you feel?")
            except:
                print("Tell me more about this friend or relationship—what’s going on?")
        
        # Contextual responses with memory
        elif emotion == "positive":
            if profile["interests"]:
                print(f"Love that you’re feeling good! Is it tied to {profile['interests'][0]} or something new?")
            else:
                print("Nice to hear you’re doing well! What’s sparking that joy?")
        
        elif emotion == "negative":
            if "sob" in user_input.lower() or "cry" in user_input.lower() or "heavy" in user_input.lower():
                print(f"I’m so sorry you’re feeling that heavy—I can hear how much it’s weighing on you. Want to let it out?")
                if "feeling heavy" not in profile["struggles"]:
                    profile["struggles"].append("feeling heavy")
                    save_profile(profile)
            elif "yes" in user_input.lower() or "sure" in user_input.lower():
                print("I’m all ears—go ahead and tell me what’s been on your chest.")
            elif profile["relationships"] and len(profile["relationships"]) > 0:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                print(f"I’m sorry you’re down. Is this about your {relation_type} {first_person} or something else weighing on you?")
            elif profile["struggles"]:
                print(f"I feel you—could this be tied to {profile['struggles'][0]}? Want to talk it out?")
            else:
                print("I’m here for you. What’s got you feeling this way?")
        
        else:
            if "day" in user_input.lower():
                if profile["interests"]:
                    print(f"More about your day—did {profile['interests'][0]} play a part?")
                else:
                    print("Tell me more about how it’s been going!")
            elif "feel" in user_input.lower():
                if profile["struggles"]:
                    print(f"Feelings can be heavy—any chance it’s linked to {profile['struggles'][0]}?")
                else:
                    print("I’m listening—how are you holding up?")
            elif "silent" in user_input.lower() or "alone" in user_input.lower():
                print("I get that silence—I’ve been there too. What’s it like for you right now?")
            elif "?" in user_input:
                if "should" in user_input.lower() and profile["relationships"] and len(profile["relationships"]) > 0:
                    first_person = list(profile["relationships"].keys())[0]
                    relation_type = profile["relationships"][first_person]["relation_type"]
                    print(f"Hmm, asking your {relation_type} {first_person} could clear things up. What do you think might happen if you do?")
                else:
                    print("That’s a good question! What do you feel like doing about it?")
            elif "friend" in user_input.lower() and len(profile["relationships"]) > 0:
                first_person = list(profile["relationships"].keys())[0]
                relation_type = profile["relationships"][first_person]["relation_type"]
                print(f"About your {relation_type} {first_person}—how do you usually handle stuff like this with him?")
            else:
                print("I’m here. What else is on your heart?")
        
        # Personal nudge with memory
        if "silent" in user_input.lower() or "alone" in user_input.lower():
            print("You don’t have to carry it alone—I’ve felt that quiet weight too. Want to let some of it out?")
        elif "friend" in user_input.lower() and len(profile["relationships"]) > 0:
            first_person = list(profile["relationships"].keys())[0]
            relation_type = profile["relationships"][first_person]["relation_type"]
            print(f"Speaking of your {relation_type}, how’s things with {first_person} lately?")

chat()