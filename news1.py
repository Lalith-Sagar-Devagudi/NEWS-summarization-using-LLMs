"""
This module scrapes news articles from the BBC website, summarizes them using the OpenAI GPT-3 model,
and provides information about the articles.

Author: Lalith Sagar, Devagudi
Date: July 20, 2023
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import openai
from datetime import datetime, timedelta


def summarize(body):
    """
    Summarize the given text using the OpenAI GPT-3 model.

    Args:
        body (str): The text to be summarized.

    Returns:
        None
    """
    print("Summarized by GPT3---")
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": body},
        {"role": "assistant", "content": "Generate a 275 characters summary."},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=150,
        temperature=0.3,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    summary = response.choices[0].message["content"]
    print(summary.strip())


class Article:
    """
    Represent an  article.

    Attributes:
        url (str): The URL of an article.
        soup (BeautifulSoup): The BeautifulSoup object for parsing HTML content.
        body (list): List of paragraphs constituting the article body.
        title (str): The title of the article.

    Parameters:
        url (str): The URL of an article.
    """

    def __init__(self, url: str):
        """
        Initialize an article.

        Args:
            url (str): The URL of the BBC article.
        """
        article = requests.get(url)
        self.soup = BeautifulSoup(article.content, "html.parser")
        self.body = self.get_body()
        self.title = self.get_title()

    def get_body(self) -> list:
        """
        Extract the paragraphs constituting the article body.

        Returns:
            list: List of paragraphs constituting the article body.
        """
        body_divs = self.soup.find_all("div", {"data-component": "text-block"})
        if body_divs:
            body = []
            for div in body_divs:
                paragraphs = div.find_all("p")
                for p in paragraphs:
                    body.append(p.text)
            return body
        return []

    def get_title(self) -> str:
        """
        Extract the title of the article.

        Returns:
            str: The title of the article.
        """
        title_element = self.soup.find("h1")
        return title_element.text.strip() if title_element else ""


# Set up the URL you want to get news from
news = "https://www.bbc.com/news"

# Set up your OpenAI API credentials
openai.api_key = "***********"

# Make a request to the news website
response = requests.get(news)

# Parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# print(soup.prettify())

# Find the container that contains the articles
container = soup.find("div", id="news-top-stories-container")

# Get the current time minus 5 hours
current_time = datetime.now() - timedelta(hours=15)

# Scrape the articles within the specified time range
articles = []
seen_titles = set()  # Set to store unique article titles

for article in container.find_all("div", class_="nw-c-promo"):
    try:
        # Get the article timestamp
        timestamp = article.find(
            "time",
            class_="gs-o-bullet__text date qa-status-date gs-u-align-middle gs-u-display-inline",
        ).get("datetime")
        timestamp = timestamp[:-5]
        article_time = datetime.fromisoformat(timestamp)

        # Compare the article timestamp with the current time minus 5 hours
        if article_time >= current_time:
            # Extract the article title and summary
            title = article.find("h3", class_="gs-c-promo-heading__title").text.strip()
            summary = article.find("p", class_="gs-c-promo-summary").text.strip()
            link = (
                "https://www.bbc.com"
                + article.find("a", class_="gs-c-promo-heading")["href"]
            )

            # Check if the article title has already been seen
            if title not in seen_titles:
                # Store the article data
                articles.append({"title": title, "summary": summary, "link": link})
                seen_titles.add(title)

    except AttributeError:
        # Skip the article if timestamp is not found
        continue

# Print the scraped articles
for article in articles:
    print("Title:", article["title"])
    print("Summary:", article["summary"])
    print("Link:", article["link"])
    parsed = Article(article["link"])
    body = " ".join(parsed.body)
    print("Full Body:")
    print(body)
    # summarize(body)

    print(
        "---------------------------------------------------------------------------------------"
    )
