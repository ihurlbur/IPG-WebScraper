from flask import Flask, render_template, request, redirect, url_for, make_response
import web_scraper
import os

app = Flask(__name__)

PAIRS_FILE = "hybrid_pairs.txt"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team = request.form.get("team", "").strip()
        brand = request.form.get("brand", "").strip()
        if team and brand:
            with open(PAIRS_FILE, "a") as f:
                f.write(f"{team},{brand}\n")
        return redirect(url_for("index"))

    pairs = []
    if os.path.exists(PAIRS_FILE):
        with open(PAIRS_FILE, "r") as f:
            pairs = [line.strip() for line in f if "," in line]

    html = render_template("index.html", pairs=pairs)
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response

@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    try:
        matched_articles = web_scraper.run_scraper(start_date=start_date, end_date=end_date)
    except Exception as e:
        return f"An error occurred while running the scraper: {e}", 500

    return render_template("results.html", articles=matched_articles)

@app.route("/remove-pair", methods=["POST"])
def remove_pair():
    pair_to_remove = request.form.get("pair")
    if pair_to_remove and os.path.exists(PAIRS_FILE):
        with open(PAIRS_FILE, "r") as f:
            lines = f.readlines()
        with open(PAIRS_FILE, "w") as f:
            for line in lines:
                if line.strip() != pair_to_remove.strip():
                    f.write(line)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
