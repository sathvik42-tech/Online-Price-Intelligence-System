import requests
import json
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

def debug_meesho(q):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://meesho.com",
        "Referer": f"https://meesho.com/search?q={q}",
    }
    payload = {
        "operationName": "SearchResultsFeed",
        "variables": {
            "filters": [],
            "page": 1,
            "query": q,
            "screen": "SEARCH",
            "searchType": "manual",
            "sortOrder": "RELEVANCE",
        },
        "query": (
            "query SearchResultsFeed($query: String!, $page: Int, $sortOrder: String, "
            "$filters: [FilterQueryInput], $screen: String, $searchType: String) { "
            "getFeedData(query: $query, page: $page, sortOrder: $sortOrder, "
            "filters: $filters, screen: $screen, searchType: $searchType) { "
            "page { products { id name price images { url } catalog { id urlSlug } } } } }"
        ),
    }
    
    try:
        resp = requests.post(
            "https://meesho.com/api/v1/products/search",
            json=payload, headers=headers, timeout=15
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_meesho("pencil")
