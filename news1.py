"""
This module provides a NewsSummarizer class for scraping and summarizing news articles from a specified website.

Author: Lalith Sagar, Devagudi
Date: July 22, 2023
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
from Article import Article
from summarize import summarize


class NewsSummarizer:
    """
    NewsSummarizer class for scraping and summarizing news articles.

    Attributes:
        articles (list): List to store scraped article details.
        seen_titles (set): Set to store unique article titles.
        url (str): The URL of the news website.

    Parameters:
        url (str): The URL of the news website.
    """

    def __init__(self, url: str):
        """
        Initialize the NewsSummarizer.

        Args:
            url (str): The URL of the news website.
        """
        self.articles = []
        self.seen_titles = set()
        self.url = url

    def get_articles(
        self,
        openai_api_key: str,
        hours: int = 5,
        body: bool = False,
        summarized: bool = False,
    ):
        """
        Get and optionally summarize news articles from the specified website within the specified time range.

        Args:
            openai_api_key (str): The OpenAI API key for authentication.
            hours (int): The number of past hours to scrape articles from.
            body (bool): Whether to include the full article body or not.
            summarized (bool): Whether to summarize the articles or not.

        Returns:
            None
        """
        current_time = datetime.now(timezone.utc)
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        container = soup.find("div", id="news-top-stories-container")

        for article in container.find_all("div", class_="nw-c-promo"):
            try:
                timestamp = article.find(
                    "time",
                    class_="gs-o-bullet__text date qa-status-date gs-u-align-middle gs-u-display-inline",
                ).get("datetime")
                timestamp = timestamp[:-5]
                article_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

                # Convert article_time to UTC timezone
                article_time = article_time.replace(tzinfo=timezone.utc)
                time_at_hours = current_time.replace(
                    hour=hours, minute=0, second=0, microsecond=0
                )

                from_time = current_time - timedelta(hours=hours)

                if article_time >= from_time:
                    title = article.find(
                        "h3", class_="gs-c-promo-heading__title"
                    ).text.strip()
                    summary = article.find(
                        "p", class_="gs-c-promo-summary"
                    ).text.strip()
                    link = urljoin(
                        self.url, article.find("a", class_="gs-c-promo-heading")["href"]
                    )

                    if title not in self.seen_titles:
                        time_diff = current_time - article_time
                        time_diff_hours, time_diff_remainder = divmod(
                            time_diff.seconds, 3600
                        )
                        time_diff_minutes, _ = divmod(time_diff_remainder, 60)
                        self.articles.append(
                            {
                                "title": title,
                                "summary": summary,
                                "link": link,
                                "time": str(time_diff_hours) + "hours ago"
                                if time_diff_hours > 0
                                else str(time_diff_minutes) + "minutes ago",
                            }
                        )
                        self.seen_titles.add(title)

            except AttributeError:
                continue
        print("Number of articles:", len(self.articles))
        for article in self.articles:
            print("Title:", article["title"])
            if "summary" in article:
                print("Summary:", article["summary"])
            print("Time:", article["time"])
            print("Link:", article["link"])
            parsed_article = Article(article["link"])
            if body and not summarized:
                body = " ".join(parsed_article.body)
                print("Body:", body)
            if summarized and openai_api_key == None:
                print("Please provide an OpenAI API key to summarize the articles.")
            elif summarized:
                body = " ".join(parsed_article.body)
                summarize(body, openai_api_key)
            print(
                "---------------------------------------------------------------------------------------"
            )


# Example usage:
openai_api_key = (
    "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"  # Replace with your API key
)

summarizer = NewsSummarizer(url="https://www.bbc.com/news")
summarizer.get_articles(
    openai_api_key=openai_api_key, hours=5, body=False, summarized=False
)
