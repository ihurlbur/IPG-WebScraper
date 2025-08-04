from flask import Flask, render_template, request, redirect, url_for, session
from web_scraper import run_scraper
import os
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

PAIRS_FILE = "hybrid_pairs.txt"
RSS_RESULTS_FILE = "rss_results.json"
SERP_RESULTS_FILE = "serp_results.json"

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

def save_pair(team, brand):
    with open(PAIRS_FILE, "a") as f:
        f.write(f"{team},{brand}\n")

def remove_pair(pair_to_remove):
    if os.path.exists(PAIRS_FILE):
        with open(PAIRS_FILE, "r") as f:
            lines = f.readlines()
        with open(PAIRS_FILE, "w") as f:
            for line in lines:
                if line.strip().lower() != pair_to_remove.lower():
                    f.write(line)

@app.route("/", methods=["GET"])
def index():
    pairs = load_pairs()
    return render_template("index.html", pairs=pairs)

@app.route("/add-pair", methods=["POST"])
def add_pair():
    team = request.form.get("team", "").strip().lower()
    brand = request.form.get("brand", "").strip().lower()
    if team and brand:
        save_pair(team, brand)
    return redirect(url_for("index"))

@app.route("/remove-pair", methods=["POST"])
def remove_pair_route():
    pair = request.form.get("pair", "")
    remove_pair(pair)
    return redirect(url_for("index"))

@app.route("/run-scraper", methods=["POST"])
def run_scraper_route():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    method = request.form.get("search_method", "rss")
    session["search_method"] = method

    try:
        results = run_scraper(start_date=start_date, end_date=end_date, method=method)
    except Exception as e:
        results = {"rss": [], "serp": [], "error": str(e)}

    if "rss" in results:
        with open(RSS_RESULTS_FILE, "w") as f:
            json.dump(results["rss"], f)
    if "serp" in results:
        with open(SERP_RESULTS_FILE, "w") as f:
            json.dump(results["serp"], f)

    return redirect(url_for("results_type"))

@app.route("/results")
def results_type():
    return render_template("resultstype.html")

@app.route("/results/rss")
def rss_team_list():
    if not os.path.exists(RSS_RESULTS_FILE):
        return render_template("Team_List.html", teams=[], method="rss")

    with open(RSS_RESULTS_FILE, "r") as f:
        articles = json.load(f)

    teams = sorted(set(article["team"] for article in articles))
    return render_template("Team_List.html", teams=teams, method="rss")

@app.route("/results/serp")
def serp_team_list():
    if not os.path.exists(SERP_RESULTS_FILE):
        return render_template("Team_List.html", teams=[], method="serp")

    with open(SERP_RESULTS_FILE, "r") as f:
        articles = json.load(f)

    teams = sorted(set(article["team"] for article in articles))
    return render_template("Team_List.html", teams=teams, method="serp")

@app.route("/results/<method>/<team>")
def show_articles(method, team):
    filename = RSS_RESULTS_FILE if method == "rss" else SERP_RESULTS_FILE

    if not os.path.exists(filename):
        return render_template("articles.html", team=team, articles=[], method=method)

    with open(filename, "r") as f:
        articles = json.load(f)

    team_articles = [a for a in articles if a["team"].lower() == team.lower()]
    return render_template("articles.html", team=team, articles=team_articles, method=method)

if __name__ == "__main__":
    app.run(debug=True)
