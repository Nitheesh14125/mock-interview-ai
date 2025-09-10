from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "supersecret"   # needed for sessions
API_BASE = "http://127.0.0.1:8000"   # FastAPI backend

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/questions", methods=["POST"])
def questions():
    topic = request.form["topic"]
    difficulty = request.form["difficulty"]
    num_questions = int(request.form["num_questions"])

    res = requests.post(f"{API_BASE}/generate_questions", json={
        "topic": topic,
        "difficulty": difficulty,
        "num_questions": num_questions
    })

    questions = res.json()["questions"]
    session["questions"] = questions
    session["answers"] = []

    return render_template("questions.html", questions=questions, q_index=0)

@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    q_index = int(request.form["q_index"])
    answer = request.form["answer"]

    # save answer in session
    answers = session.get("answers", [])
    answers.append({
        "question": session["questions"][q_index],
        "answer": answer
    })
    session["answers"] = answers

    # check if more questions left
    if q_index + 1 < len(session["questions"]):
        return render_template("questions.html", questions=session["questions"], q_index=q_index+1)
    else:
        res = requests.post(f"{API_BASE}/evaluate", json={"qa_pairs": session["answers"]})
        feedback = res.json()["feedback"]
        return render_template("results.html", feedback=feedback)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
