"""
tech-digest: A daily tech digest generator that aggregates trending GitHub repos, 
             arXiv AI papers, Hacker News, and Reddit side-project highlights.

Usage:
    python tech_digest.py --output digest.md
    python tech_digest.py --output digest.md --telegram <token> --chat-id <id>

Requirements:
    - requests
    - stdlib

API Keys:
    - GITHUB_API_KEY: GitHub API key (optional)
    - ARXIV_API_KEY: arXiv API key (optional)
    - HACKERNEWS_API_KEY: Hacker News API key (optional)
    - REDDIT_API_KEY: Reddit API key (optional)
    - TELEGRAM_TOKEN: Telegram bot token (optional)
    - TELEGRAM_CHAT_ID: Telegram chat ID (optional)
"""

import argparse
import json
import os
import requests
from typing import List, Tuple
from urllib.parse import urljoin

def get_github_trending_repos() -> List[Tuple[str, int, str]]:
    """
    Get trending GitHub repos.
    
    Returns:
        List[Tuple[str, int, str]]: List of tuples containing repo name, stars, and description.
    """
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "stars:>1000",
        "sort": "stars",
        "order": "desc"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return [(item["name"], item["stargazers_count"], item["description"]) for item in data["items"]]

def get_arxiv_ai_papers() -> List[Tuple[str, str, str]]:
    """
    Get recent AI arXiv papers.
    
    Returns:
        List[Tuple[str, str, str]]: List of tuples containing paper title, authors, and abstract snippet.
    """
    url = "http://export.arxiv.org/rss/ai"
    response = requests.get(url)
    response.raise_for_status()
    data = response.text
    # Parse RSS feed using stdlib
    import xml.etree.ElementTree as ET
    root = ET.fromstring(data)
    papers = []
    for item in root.findall(".//item"):
        title = item.find("title").text
        authors = item.find("author").text
        abstract = item.find("summary").text
        papers.append((title, authors, abstract))
    return papers

def get_hackernews_top_posts() -> List[Tuple[str, str, int]]:
    """
    Get top Hacker News posts.
    
    Returns:
        List[Tuple[str, str, int]]: List of tuples containing post title, URL, and score.
    """
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    response.raise_for_status()
    story_ids = response.json()
    posts = []
    for story_id in story_ids[:10]:
        url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        response = requests.get(url)
        response.raise_for_status()
        post = response.json()
        title = post["title"]
        url = post["url"]
        score = post["score"]
        posts.append((title, url, score))
    return posts

def get_reddit_side_project_highlights() -> List[Tuple[str, str, int]]:
    """
    Get top Reddit side-project highlights.
    
    Returns:
        List[Tuple[str, str, int]]: List of tuples containing post title, link, and upvotes.
    """
    url = "https://www.reddit.com/r/sideproject/.json"
    response = requests.get(url, headers={"User-Agent": "tech-digest"})
    response.raise_for_status()
    data = response.json()
    posts = []
    for post in data["data"]["children"]:
        title = post["data"]["title"]
        link = post["data"]["url"]
        upvotes = post["data"]["ups"]
        posts.append((title, link, upvotes))
    return posts

def generate_digest(github_repos: List[Tuple[str, int, str]], 
                    arxiv_papers: List[Tuple[str, str, str]], 
                    hackernews_posts: List[Tuple[str, str, int]], 
                    reddit_posts: List[Tuple[str, str, int]]) -> str:
    """
    Generate Markdown digest.
    
    Args:
        github_repos (List[Tuple[str, int, str]]): List of GitHub repos.
        arxiv_papers (List[Tuple[str, str, str]]): List of arXiv papers.
        hackernews_posts (List[Tuple[str, str, int]]): List of Hacker News posts.
        reddit_posts (List[Tuple[str, str, int]]): List of Reddit posts.
    
    Returns:
        str: Markdown digest.
    """
    digest = "# Daily Tech Digest\n\n"
    digest += "## Trending GitHub Repos\n\n"
    for repo in github_repos:
        digest += f"* {repo[0]} ({repo[1]} stars): {repo[2]}\n"
    digest += "\n## Latest AI arXiv Papers\n\n"
    for paper in arxiv_papers:
        digest += f"* {paper[0]} by {paper[1]}\n{paper[2]}\n\n"
    digest += "\n## Hacker News Top Posts\n\n"
    for post in hackernews_posts:
        digest += f"* [{post[0]}]({post[1]}) ({post[2]} points)\n"
    digest += "\n## Reddit Side-Project Highlights\n\n"
    for post in reddit_posts:
        digest += f"* [{post[0]}]({post[1]}) ({post[2]} upvotes)\n"
    return digest

def post_to_telegram(digest: str, token: str, chat_id: str) -> None:
    """
    Post digest to Telegram.
    
    Args:
        digest (str): Markdown digest.
        token (str): Telegram bot token.
        chat_id (str): Telegram chat ID.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": digest,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

def main() -> None:
    parser = argparse.ArgumentParser(description="Daily tech digest generator")
    parser.add_argument("--output", default="digest.md", help="Output file")
    parser.add_argument("--telegram", help="Telegram bot token")
    parser.add_argument("--chat-id", help="Telegram chat ID")
    args = parser.parse_args()
    
    github_repos = get_github_trending_repos()
    arxiv_papers = get_arxiv_ai_papers()
    hackernews_posts = get_hackernews_top_posts()
    reddit_posts = get_reddit_side_project_highlights()
    
    digest = generate_digest(github_repos, arxiv_papers, hackernews_posts, reddit_posts)
    
    with open(args.output, "w") as f:
        f.write(digest)
    
    if args.telegram and args.chat_id:
        post_to_telegram(digest, args.telegram, args.chat_id)

if __name__ == "__main__":
    main()