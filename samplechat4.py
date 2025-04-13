from textblob import TextBlob
import json
import os
from datetime import datetime
import random
from vosk import Model, KaldiRecognizer
import pyaudio
import pyttsx3
import time
import tkinter as tk
from tkinter import scrolledtext, Entry, ttk, Canvas, Label

# Initialize pyttsx3 for offline TTS
engine = pyttsx3.init()

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
    if "not" in text_lower or "bad" in text_lower or "low" in text_lower or "heavy" in text_lower or "demot" in text_lower or analysis.sentiment.polarity < 0:
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
    emotions = set()
    entry_parts = []
    intentions = set()
    
    for user_input, bot_response in conversation_log:
        emotion = analyze_emotion(user_input)
        if emotion != "neutral":
            emotions.add(f"felt {emotion.replace('positive', 'good').replace('negative', 'low')}")
        
        user_lower = user_input.lower()
        if "feel" in user_lower or "felt" in user_lower:
            if not any(user_input in part for part in entry_parts):
                entry_parts.append(user_input)
        elif "friend" in user_lower or "relationship" in user_lower:
            words = user_lower.split()
            try:
                relation_type = "friend" if "friend" in words else "relationship"
                name_idx = words.index(relation_type) + 1
                name = words[name_idx]
                issue = " ".join(words[name_idx + 1:]) if name_idx + 1 < len(words) else "mentioned"
                rel_str = f"about my {relation_type} {name} ({issue})"
                if rel_str not in entry_parts:
                    entry_parts.append(rel_str)
            except:
                if user_input not in entry_parts:
                    entry_parts.append(user_input)
        elif "like" in user_lower or "enjoy" in user_lower:
            words = user_lower.split()
            try:
                keyword = next(word for word in ["like", "enjoy"] if word in user_lower)
                thing_idx = words.index(keyword) + 1
                thing = " ".join(words[thing_idx:thing_idx + 2]) if thing_idx + 1 < len(words) else words[thing_idx]
                if thing not in ["to", "the", "a", "and"]:
                    enjoy_str = f"enjoyed {thing}"
                    if enjoy_str not in entry_parts:
                        entry_parts.append(enjoy_str)
            except:
                if user_input not in entry_parts:
                    entry_parts.append(user_input)
        elif "want" in user_lower or "wanted" in user_lower:
            intent = user_input.split("want", 1)[-1].strip()
            intentions.add(intent)

    if not emotions and not entry_parts and not intentions:
        return "Not much to say today—just chatted with Issabela."
    
    entry = []
    if emotions:
        emotion_str = " and ".join(sorted(emotions))
        entry.append(f"I {emotion_str} today")
    if entry_parts:
        parts_str = ", ".join(entry_parts)
        entry.append(parts_str)
    if intentions:
        intent_str = " and ".join(sorted(intentions))
        entry.append(f"and wanted to {intent_str}")

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

# Convert text to speech offline
def speak(text, chatbot_name):
    engine.say(f"{chatbot_name} says: {text}")
    engine.runAndWait()

# Get voice input offline using Vosk with Indian English model
def get_voice_input(chat_window):
    model_path = "model/vosk-model-small-en-in-0.4"  # Updated to Indian English model
    if not os.path.exists(model_path):
        chat_window.insert(tk.END, "[Error: Vosk model not found. Please download it.]\n")
        chat_window.see(tk.END)
        return None
    
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    chat_window.insert(tk.END, "[Listening...]\n")
    chat_window.see(tk.END)
    root.update()

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    chat_window.insert(tk.END, f"[You (voice): {text}]\n")
                    chat_window.see(tk.END)
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return text
            time.sleep(0.1)
    except Exception as e:
        chat_window.insert(tk.END, f"[Error: {str(e)}]\n")
        chat_window.see(tk.END)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    return None

# Chat logic with enhanced GUI
def chat():
    global profile, root, chat_window, input_box, send_button, speak_button, header_label
    profile = load_profile()
    last_mentioned_friend = None
    conversation_log = []

    root = tk.Tk()
    root.title("Issabela Chat")
    root.geometry("700x500")

    # Gradient background
    canvas = Canvas(root, width=700, height=500)
    canvas.pack(fill="both", expand=True)
    canvas.create_rectangle(0, 0, 700, 500, fill="#BBDEFB", outline="")
    canvas.create_rectangle(0, 0, 700, 250, fill="#1976D2", outline="")

    # Header
    header_frame = tk.Frame(canvas, bg="#1976D2", relief="raised", bd=2)
    header_frame.place(x=0, y=0, width=700)
    header_label = tk.Label(header_frame, text="Chat with Issabela", font=("Helvetica", 16, "bold"), fg="white", bg="#1976D2", pady=10)
    header_label.pack()

    # Chat display with bubbles
    chat_frame = tk.Frame(canvas, bg="#FFFFFF", relief="sunken", bd=2)
    chat_frame.place(x=20, y=60, width=660, height=380)
    chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, width=80, height=25, bg="#FFFFFF", fg="#212121", font=("Segoe UI", 10), borderwidth=0)
    chat_window.pack(padx=10, pady=10)
    chat_window.tag_config("user", foreground="#388E3C", justify="right")
    chat_window.tag_config("bot", foreground="#1976D2", justify="left")

    # Input frame
    input_frame = tk.Frame(canvas, bg="#BBDEFB")
    input_frame.place(x=20, y=450, width=660, height=40)

    input_box = Entry(input_frame, width=40, font=("Segoe UI", 11), bg="#FFFFFF", fg="#212121", relief="flat", borderwidth=2)
    input_box.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

    style = ttk.Style()
    style.configure("Send.TButton", font=("Segoe UI", 10, "bold"), padding=6, background="#388E3C", foreground="white")
    style.map("Send.TButton", background=[("active", "#2E7D32")])
    style.configure("Speak.TButton", font=("Segoe UI", 10, "bold"), padding=6, background="#1976D2", foreground="white")
    style.map("Speak.TButton", background=[("active", "#1565C0")])

    send_button = ttk.Button(input_frame, text="Send", command=lambda: process_input(False), style="Send.TButton")
    send_button.grid(row=0, column=1, padx=5, pady=5)

    speak_button = ttk.Button(input_frame, text="Speak", command=lambda: process_input(True), style="Speak.TButton")
    speak_button.grid(row=0, column=2, padx=5, pady=5)

    input_frame.grid_columnconfigure(0, weight=1)

    # Initial setup
    if not profile["user_name"]:
        chat_window.insert(tk.END, "Hi! I’m your companion. What’s your name?\n", "bot")
        process_initial_input("user_name")
    elif not profile["chatbot_name"]:
        chat_window.insert(tk.END, f"Hi {profile['user_name']}! What would you like to call me?\n", "bot")
        process_initial_input("chatbot_name")
    else:
        start_chat(conversation_log)

    root.mainloop()

def process_initial_input(field):
    def submit():
        text = input_box.get().strip()
        if text:
            profile[field] = text
            save_profile(profile)
            chat_window.delete(1.0, tk.END)
            if field == "user_name":
                chat_window.insert(tk.END, f"Hi {profile['user_name']}! What would you like to call me?\n", "bot")
                process_initial_input("chatbot_name")
            else:
                header_label.config(text=f"{profile['user_name']} & {profile['chatbot_name']}")
                start_chat([])
        input_box.delete(0, tk.END)
    
    input_box.bind("<Return>", lambda event: submit())
    send_button.config(command=submit)

def start_chat(conversation_log):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    day = now.strftime("%A")
    diary_file = "digital_diary.txt"
    with open(diary_file, "a") as file:
        file.write(f"\n[{date} - {day}]\n")
    
    greeting = f"Hi {profile['user_name']}! I’m {profile['chatbot_name']}, here to listen and help. How’s your day going?"
    chat_window.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {profile['chatbot_name']}: {greeting}\n", "bot")
    speak(greeting, profile["chatbot_name"])

def process_input(use_voice):
    user_input = get_voice_input(chat_window) if use_voice else input_box.get().strip()
    input_box.delete(0, tk.END)
    if not user_input:
        return
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    chat_window.insert(tk.END, f"[{time_str}] Me: {user_input}\n", "user")
    chat_window.see(tk.END)
    root.update()

    conversation_log = root.__dict__.setdefault("conversation_log", [])
    last_mentioned_friend = root.__dict__.setdefault("last_mentioned_friend", None)

    if user_input.lower() in ["bye", "goodbye", "see you"]:
        farewell = f"Alright, take care! I’m {profile['chatbot_name']}—always here if you need me."
        chat_window.insert(tk.END, f"[{time_str}] {profile['chatbot_name']}: {farewell}\n", "bot")
        speak(farewell, profile["chatbot_name"])
        log_conversation("digital_diary.txt", user_input, farewell)
        conversation_log.append((user_input, farewell))
        write_diary_entry("digital_diary.txt", conversation_log)
        save_profile(profile)
        root.quit()
        return
    
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
    elif user_input.lower() in ["nahh", "nope", "no", "nvm", "nah"]:
        response = f"Okay, great! I’m {profile['chatbot_name']}—let me know if you need any assistance or just want to chat later. {make_suggestion(profile, emotion)}"
    elif "like" in user_input.lower() or "interest" in user_input.lower() or "enjoy" in user_input.lower():
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
        except:
            response = "I caught that you enjoy something—what is it you’re into?"
    elif "struggle" in user_input.lower() or "hard" in user_input.lower():
        thing = user_input.split("struggle" if "struggle" in user_input.lower() else "hard")[-1].strip()
        if thing not in profile["struggles"]:
            profile["struggles"].append(thing)
            save_profile(profile)
        response = f"That sounds tough—{thing} is no joke. How can I support you with it?"
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
        except:
            response = "Tell me more about this friend or relationship—what’s going on?"
    elif emotion == "positive":
        response = f"Love that you’re feeling good! Is it tied to {profile['interests'][-1]} or something new?" if profile["interests"] else "Nice to hear you’re doing well! What’s sparking that joy?"
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

    chat_window.insert(tk.END, f"[{time_str}] {profile['chatbot_name']}: {response}\n", "bot")
    chat_window.see(tk.END)
    speak(response, profile["chatbot_name"])
    log_conversation("digital_diary.txt", user_input, response)
    conversation_log.append((user_input, response))
    root.__dict__["conversation_log"] = conversation_log
    root.__dict__["last_mentioned_friend"] = last_mentioned_friend

    if "silent" in user_input.lower() or "alone" in user_input.lower():
        response = f"You don’t have to carry it alone—I’ve felt that quiet weight too. Want to let some of it out? {make_suggestion(profile, emotion)}"
        chat_window.insert(tk.END, f"[{time_str}] {profile['chatbot_name']}: {response}\n", "bot")
        speak(response, profile["chatbot_name"])
        log_conversation("digital_diary.txt", user_input, response)
        conversation_log.append((user_input, response))
    elif "friend" in user_input.lower() and profile["relationships"]:
        first_person = random.choice(list(profile["relationships"].keys()))
        relation_type = profile["relationships"][first_person]["relation_type"]
        response = f"Speaking of your {relation_type}, how’s things with {first_person} lately? {make_suggestion(profile, emotion)}"
        chat_window.insert(tk.END, f"[{time_str}] {profile['chatbot_name']}: {response}\n", "bot")
        speak(response, profile["chatbot_name"])
        log_conversation("digital_diary.txt", user_input, response)
        conversation_log.append((user_input, response))

if __name__ == "__main__":
    chat()