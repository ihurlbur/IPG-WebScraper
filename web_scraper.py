import feedparser
from datetime import datetime, timedelta
import re
import json

def run_scraper():
    # Load team-brand pairs from text file
    with open("hybrid_pairs.txt", "r") as f:
        lines = f.readlines()
        pairs = [tuple(line.strip().lower().split(", ")) for line in lines]

    # Create a unique list of teams
    teams = sorted(set(team for team, _ in pairs))

    # Keywords to search alongside team names
    keywords = ["sponsorship", "partnership", "deal", "agreement", "contract", "negotiation"]

    # Only include articles from the past 30 days
    cutoff_date = datetime.now() - timedelta(days=30)

    # To avoid duplicates
    seen = set()
    matched_articles = []

    for team in teams:
        for keyword in keywords:
            query = f"{team} {keyword}"
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link", "").strip()

                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except Exception:
                    continue

                if pub_date < cutoff_date:
                    continue

                uid = (title.lower(), link)
                if uid in seen:
                    continue
                seen.add(uid)

                # Combine and sanitize title + summary
                content = f"{title} {summary}".lower()
                content = re.sub(r"[^\w\s]", "", content)

                # Check for any matching team-brand pair in the content
                for t, brand in pairs:
                    if t in content and brand in content:
                        matched_articles.append({
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "team": t,
                            "brand": brand,
                            "title": title,
                            "link": link
                        })
                        break  # avoid duplicate checks

    # Save results
    with open("matched_articles.json", "w") as f:
        json.dump(matched_articles, f, indent=2)

    return matched_articles
