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

# Step 3: Summarize Using GPT-4 (Updated API)
def summarize_posts(posts):
    if not posts:
        return


# Step 4: Run the Agent
if __name__ == "__main__":
    blog_posts = scrape_blog(COMPETITOR_BLOG_URL)
    new_posts = detect_new_posts(blog_posts)
    summary = summarize_posts(new_posts)

    log_message = f"\n### Competitive Intelligence Update ###\n{summary}\n"

    # Force output to GitHub Actions logs
    print("=" * 50)
    print(log_message)
    print("=" * 50)

    # Save output to a log file
    with open("latest_report.txt", "w", encoding="utf-8") as log_file:
        log_file.write(log_message)

