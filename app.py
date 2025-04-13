from flask import Flask, render_template, request, jsonify
from llmchatbot import generate_response, analyze_emotion, load_profile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    try:
        data = request.json
        user_input = data['input']
        profile = load_profile()
        emotion = analyze_emotion(user_input)
        response = generate_response(user_input, emotion, profile)
        return jsonify({
            'response': response,
            'emotion': emotion,
            'language': profile.get('language', 'en')
        })
    except Exception as e:
        return jsonify({'response': 'Error processing input.', 'emotion': 'neutral', 'language': 'en'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)