import requests
from bs4 import BeautifulSoup
import json
import openai
import os

# Load API Key from GitHub Secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Competitor Blog URL (Change this to your competitor's blog)
COMPETITOR_BLOG_URL = "https://www.workday.com/blog"

# Storage file to track seen blog posts
STORAGE_FILE = "seen_blogs.json"

# Step 1: Scrape the Blog Page
def scrape_blog(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article")  # Change this if blog structure is different

        blog_posts = []
        for article in articles:
            title = article.find("h2").get_text(strip=True) if article.find("h2") else "No Title"
            link = article.find("a")["href"] if article.find("a") else "No Link"
            blog_posts.append({"title": title, "link": link})

        return blog_posts
    return []

# Step 2: Detect New Blog Posts
def detect_new_posts(blog_posts):
    try:
        with open(STORAGE_FILE, "r") as f:
            seen_posts = json.load(f)
    except FileNotFoundError:
        seen_posts = []

    new_posts = [post for post in blog_posts if post not in seen_posts]

    # Update storage with latest blog posts
    with open(STORAGE_FILE, "w") as f:
        json.dump(blog_posts, f)

    return new_posts

# Step 3: Summarize Using GPT-4
def summarize_posts(posts):
    if not posts:
        return "No new blog updates detected."

    openai.api_key = OPENAI_API_KEY
    summaries = []

    for post in posts:
        prompt = f"Summarize this competitor blog post:\nTitle: {post['title']}\nLink: {post['link']}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI summarizing competitive intelligence blog posts."},
                {"role": "
