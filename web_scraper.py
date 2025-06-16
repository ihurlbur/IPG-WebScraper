def run_scraper():
    pairs = load_pairs()
    all_matches = []
    base_url = "https://news.google.com/rss/search?q={}+{}+sponsorship"

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    for team, brand in pairs:
        url = base_url.format(team.replace(" ", "+"), brand.replace(" ", "+"))
        feed = feedparser.parse(url)

        for entry in feed.entries:
            try:
                published = datetime(*entry.published_parsed[:6])
            except AttributeError:
                continue  # Skip if no date

            if published >= thirty_days_ago:
                summary = entry.get("summary", "").lower()
                title = entry.get("title", "").lower()

                # 🔍 DEBUG PRINT
                print(f"📝 Scanning: {title} | Summary: {summary}")

                if team in summary or team in title:
                    if brand in summary or brand in title:
                        all_matches.append({
                            "team": team,
                            "brand": brand,
                            "title": entry.title,
                            "link": entry.link,
                            "published": published.strftime("%Y-%m-%d")
                        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_matches, f, indent=2)
