from textblob import TextBlob

def analyze_emotion(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"

def save_journal(entry):
    with open("digital_diary.txt", "a") as file:
        file.write(f"{entry}\n")

def chat():
    print("Hi! I’m here to listen. How are you feeling?")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "bye":
            print("Take care! I’m always here if you need me.")
            break
        emotion = analyze_emotion(user_input)
        save_journal(user_input)
        if emotion == "positive":
            print("I’m glad you’re feeling good! What’s making you happy?")
        elif emotion == "negative":
            print("I’m sorry you’re feeling that way. Want to tell me more?")
        else:
            print("I’m here with you. What’s on your mind?")

chat()