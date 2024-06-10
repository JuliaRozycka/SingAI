from flask import Flask, render_template, jsonify, request
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import ollama
from GestureRecognizer import GestureRecognizer

app = Flask(__name__)

model_name = 'gpt2-large'
# Load pre-trained model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
recognizer = GestureRecognizer()

polish_to_english = {
    'Pogotowie': 'Ambulance',
    'Lekarz': 'Doctor',
    'Zawal': 'Heart attack',
    'Lekarstwo': 'Medicine',
    'Pomoc': 'Help',
    'Telefon': 'Call',
    'Potrzebowac': 'Need',
    'Pozar': 'Fire',
    'Zatrucie': 'Poisoning',
    'Szpital': 'Hospital',
    'Bol': 'Pain',
}


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/generate_sentence", methods=["POST"])
def generate_sentence():
    words = request.json.get("words")

    if not words:
        return jsonify({'error': 'No words provided'}), 400

    english_words = [polish_to_english.get(word, word) for word in words]

    prompt = (
        f"Imagine you are in an emergency situation and need to communicate using these words. Create one sentence in the first person using these words: {', '.join(english_words[-2:])}."
    )

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return jsonify({"sentence": response["message"]["content"].replace('"', '')})


@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.get_json()
    data_url = data.get('data_url', None)
    if not data_url:
        return jsonify({'error': 'No frame data provided'}), 400

    result = recognizer.process_video(data_url)
    return jsonify(result)
