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

def scrape_blog(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article")  # Change this if needed

        blog_posts = []
        for article in articles:
            title_tag = article.find("h2") or article.find("h3")  # Check both <h2> and <h3>
            title = title_tag.get_text(strip=True) if title_tag else "Untitled Post"

            link_tag = article.find("a")
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else "No Link"

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

import openai

def summarize_posts(posts):
    if not posts:
        return "No new blog updates detected."

    openai.api_key = OPENAI_API_KEY
    summaries = []

    for post in posts:
        try:
            prompt = f"Summarize this competitor blog post:\nTitle: {post['title']}\nLink: {post['link']}"

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI summarizing competitor blog posts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Fix API response parsing for OpenAI v1.0+
            summary = response["choices"][0]["message"]["content"]
            summaries.append(f"🔹 **{post['title']}**\n{summary}\n🔗 {post['link']}\n")

        except Exception as e:
            summaries.append(f"🔹 **{post['title']}**\n⚠ Failed to summarize: {str(e)}\n🔗 {post['link']}\n")

    return "\n".join(summaries)



# Step 4: Run the Agent
if __name__ == "__main__":
    print("\n🔍 Running Competitive Intelligence Agent...\n")

    blog_posts = scrape_blog(COMPETITOR_BLOG_URL)
    print("\n📢 RAW SCRAPED BLOG POSTS:")
    print(blog_posts)  # Debugging: Print raw extracted data

    new_posts = detect_new_posts(blog_posts)
    print("\n🆕 DETECTED NEW POSTS:")
    print(new_posts)  # Debugging: Print only new posts

    summary = summarize_posts(new_posts)

    log_message = f"\n### Competitive Intelligence Update ###\n{summary}\n"

    # Force output to GitHub Actions logs
    print("=" * 50)
    print(log_message)
    print("=" * 50)

    # Save output to a log file
    with open("latest_report.txt", "w", encoding="utf-8") as log_file:
        log_file.write(log_message)

    print("\n✅ Execution Complete. Check 'latest_report.txt' for results.\n")

