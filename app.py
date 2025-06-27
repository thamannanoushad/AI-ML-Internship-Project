from flask import Flask, render_template, request,session, redirect, url_for
from transformers import pipeline
import textstat

app = Flask(__name__)
app.secret_key="secret123abc"
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(text):
    if len(text.split()) < 50:
        return "Text too short to summarize.", {"word_count": 0, "readability": 0}
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = [summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] for chunk in chunks]
    summary = ' '.join(summaries)
    return summary, {"word_count": len(summary.split()), "readability": round(textstat.flesch_reading_ease(summary), 2)}

@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        text = request.form.get("article", "")
        summary, metrics = generate_summary(text)
        
        session["history"].append({
            "input": text[:100] + "..." if len(text) > 100 else text,
            "summary": summary,
            "metrics": metrics
        })
        session.modified = True

        session["summary"] = summary
        session["metrics"] = metrics
        return redirect(url_for("index"))

    summary = session.pop("summary", None)
    metrics = session.pop("metrics", None)
    history = session.get("history", [])
    return render_template("index.html", summary=summary, metrics=metrics, history=history)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop("history", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
