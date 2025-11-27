from flask import Flask, request, jsonify, render_template_string
import subprocess

app = Flask(__name__)

def run_deepseek(prompt):
    """Run DeepSeek model via Ollama and return output"""
    result = subprocess.run(
        ["ollama", "run", "deepseek-r1:1.5b", prompt],
        capture_output=True, text=True, encoding='utf-8',    
        errors='replace' 
    )
    return result.stdout.strip()

@app.route("/", methods=["GET", "POST"])
def home():
    answer = None
    related_questions = []
    question = None

    if request.method == "POST":
        question = request.form["question"]

        # Step 1: Get answer
        answer = run_deepseek(f"Answer this question clearly:\n\n{question}")

        # Step 2: Get related questions
        related_prompt = f"Based on the question '{question}' and its answer '{answer}', suggest 3 related follow-up questions."
        related_questions = run_deepseek(related_prompt).split("\n")

    # HTML template inside Python
    html = """
   <!DOCTYPE html>
<html>
<head>
    <title>DeepSeek</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        input[type=text] { width: 400px; padding: 10px; }
        button { padding: 10px; }
        .answer, .related { margin-top: 20px; font-size: 18px; }
    </style>
</head>
<body>
    <h1>Welcome to DeepSeek</h1>

    <form method="POST">
        <input type="text" name="question" placeholder="Ask a question" value="{{ question if question else '' }}">
        <button type="submit">Ask</button>
    </form>

    {% if answer %}
        <div class="answer">
            <p><strong>Answer:</strong> {{ answer }}</p>
        </div>
    {% endif %}

    {% if related_questions %}
        <div class="related">
            <p><strong>Related Questions:</strong></p>
            <ul>
                {% for q in related_questions %}
                    <li>{{ q }}</li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
</body>
</html>
    """
    return render_template_string(html, answer=answer, related_questions=related_questions, question=question)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
