import os
import feedparser
import requests
from datetime import datetime
from serpapi import GoogleSearch
from urllib.parse import quote

PAIRS_FILE = "hybrid_pairs.txt"
SERPAPI_API_KEY = "f72e1fe42956be83d8c3617dc870968da7f315eee43e0502a9e1c93e1feda716"  # Make sure this is set in your environment

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

def run_rss_search(start_date=None, end_date=None):
    results = []
    pairs = load_pairs()

    for team, brand in pairs:
        query = f"{team} {brand} sponsorship"
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            try:
                published_date = datetime(*entry.published_parsed[:6]).date()
                if start_date and published_date < datetime.strptime(start_date, "%Y-%m-%d").date():
                    continue
                if end_date and published_date > datetime.strptime(end_date, "%Y-%m-%d").date():
                    continue

                title = entry.title
                summary = entry.summary if hasattr(entry, "summary") else ""
                if team.lower() in (title + summary).lower() and brand.lower() in (title + summary).lower():
                    results.append({
                        "team": team.title(),
                        "brand": brand.title(),
                        "title": title,
                        "link": entry.link,
                        "published": published_date.strftime("%Y-%m-%d"),
                    })
            except Exception as e:
                continue  # skip malformed entries

    return results

def run_serpapi_search(start_date=None, end_date=None):
    if not SERPAPI_API_KEY:
        return [{
            "team": "Error", 
            "brand": "Error", 
            "title": "SerpAPI key not set", 
            "link": "#", 
            "published": ""
        }]
    
    results = []
    pairs = load_pairs()

    for team, brand in pairs:
        query = f"{team} {brand} sponsorship"

        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
            "num": 20,
        })

        serp_results = search.get_dict()
        for result in serp_results.get("organic_results", []):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            date_str = result.get("date", "")

            if not title or not link:
                continue

            if team.lower() in (title + snippet).lower() and brand.lower() in (title + snippet).lower():
                published = ""
                try:
                    if start_date or end_date:
                        if date_str:
                            published_date = datetime.strptime(date_str, "%b %d, %Y").date()
                            if start_date and published_date < datetime.strptime(start_date, "%Y-%m-%d").date():
                                continue
                            if end_date and published_date > datetime.strptime(end_date, "%Y-%m-%d").date():
                                continue
                            published = published_date.strftime("%Y-%m-%d")
                except:
                    pass  # fallback to blank publish date if formatting fails

                results.append({
                    "team": team.title(),
                    "brand": brand.title(),
                    "title": title,
                    "link": link,
                    "published": published,
                })

    return results

def run_scraper(start_date=None, end_date=None, method="rss"):
    if method == "rss":
        return {
            "rss": run_rss_search(start_date, end_date),
            "serp": []
        }
    elif method == "serpapi":
        return {
            "rss": [],
            "serp": run_serpapi_search(start_date, end_date)
        }
    elif method == "both":
        return {
            "rss": run_rss_search(start_date, end_date),
            "serp": run_serpapi_search(start_date, end_date)
        }
    else:
        return {
            "rss": [],
            "serp": [],
            "error": f"Invalid method: {method}"
        }

