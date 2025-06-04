from flask import Flask, render_template, request, redirect, url_for
import os
import json
import web_scraper  # ✅ Make sure web_scraper.py exists in the same directory

app = Flask(__name__)

PAIRS_FILE = "hybrid_pairs.txt"
RESULT_FILE = "matched_articles.json"

def load_pairs():
    pairs = []
    if os.path.exists(PAIRS_FILE):
        with open(PAIRS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and "," in line:
                    parts = [p.strip().lower() for p in line.split(",")]
                    if len(parts) == 2:
                        pairs.append(tuple(parts))
    return pairs

def save_pairs(pairs):
    with open(PAIRS_FILE, "w") as f:
        for team, brand in pairs:
            f.write(f"{team}, {brand}\n")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team = request.form.get("team", "").strip().lower()
        brand = request.form.get("brand", "").strip().lower()
        if team and brand:
            pairs = load_pairs()
            if (team, brand) not in pairs:
                pairs.append((team, brand))
                save_pairs(pairs)
        return redirect(url_for("index"))

    pairs = load_pairs()
    return render_template("index.html", pairs=pairs)

@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    matched_articles = web_scraper.run_scraper()
    with open(RESULT_FILE, "w") as f:
        json.dump(matched_articles, f, indent=2)
    return render_template("results.html", articles=matched_articles)

@app.route("/results")
def results():
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r") as f:
            articles = json.load(f)
    else:
        articles = []
    return render_template("results.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)

