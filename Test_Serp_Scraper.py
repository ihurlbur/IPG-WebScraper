from serpapi import GoogleSearch

# Replace this with your actual SerpAPI key
SERPAPI_KEY = "f72e1fe42956be83d8c3617dc870968da7f315eee43e0502a9e1c93e1feda716"

def search_partnership_news(team, brand):
    query = f"{team} {brand} sponsorship OR partnership OR deal"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 10,  # number of results to return
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    articles = []
    for result in results.get("organic_results", []):
        article = {
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet", ""),
            "displayed_link": result.get("displayed_link", "")
        }
        articles.append(article)

    return articles


if __name__ == "__main__":
    team = input("Enter team name: ")
    brand = input("Enter brand name: ")
    articles = search_partnership_news(team, brand)

    if articles:
        print(f"\nTop results for '{team} + {brand}':\n")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   {article['link']}")
            print(f"   {article['snippet']}\n")
    else:
        print("No results found.")
