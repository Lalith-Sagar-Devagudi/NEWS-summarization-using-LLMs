"""
This module provides a BBCNewsSummarizer class for scraping and summarizing news articles from a specified website.

Author: Lalith Sagar, Devagudi
Date: July 22, 2023
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
from Article import Article
from summarize import summarize


class BBCNewsSummarizer:
    """
    BBCNewsSummarizer class for scraping and summarizing news articles.

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
        hours: int = None,
        category: str = None,
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

        # Handle category-specific scraping
        if category:
            self.url = self.url + "/" + category.lower()
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, "html.parser")
            container = soup.find("div", id="topos-component")
        else:
            container = soup.find("div", id="news-top-stories-container")

        # If hours is None, fetch all articles without filtering by time range
        if hours is None:
            from_time = datetime.min.replace(
                tzinfo=timezone.utc
            )  # Start from the earliest possible time
        else:
            current_time = datetime.now(timezone.utc)
            from_time = current_time - timedelta(hours=hours)

        # Scraping articles from the selected container
        for article in container.find_all("div", class_="nw-c-promo"):
            try:
                # Extracting timestamp from the article
                timestamp = article.find("time").get("datetime")
                timestamp = timestamp[:-5]
                if timestamp:
                    article_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                    article_time = article_time.replace(tzinfo=timezone.utc)
                else:
                    article_time = from_time

                if article_time >= from_time:
                    title = article.find(
                        "h3", class_="gs-c-promo-heading__title"
                    ).text.strip()
                    summary_tag = article.find("p", class_="gs-c-promo-summary")
                    summary = summary_tag.text.strip() if summary_tag else ""
                    link = urljoin(
                        self.url, article.find("a", class_="gs-c-promo-heading")["href"]
                    )

                    # Add the article to the list if the title is unique
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
                                "time": f"{time_diff_hours} hours ago"
                                if time_diff_hours > 0
                                else f"{time_diff_minutes} minutes ago",
                            }
                        )
                        self.seen_titles.add(title)

            except AttributeError:
                continue

        # Printing the scraped articles
        print("Number of articles:", len(self.articles))
        for article in self.articles:
            print("Title:", article["title"])
            if "summary" in article:
                print("Summary:", article["summary"])
            # print("Time:", article["time"])
            print("Link:", article["link"])
            inside_article = requests.get(article["link"])
            inside_soup = BeautifulSoup(inside_article.content, "html.parser")
            parsed_article = Article(inside_soup)
            print("Inside Link Title:", parsed_article.title)
            # If body is requested and summarization is not needed
            if body and not summarized:
                body_text = " ".join(parsed_article.body)
                print("Body:", body_text)

            # If summarization is requested and the API key is provided
            if summarized and openai_api_key:
                body_text = " ".join(parsed_article.body)
                summarize(body_text, openai_api_key)
                # Note: The summarized text will be printed by the 'summarize' function.

            print(
                "---------------------------------------------------------------------------------------"
            )

    def get_categories(self):
        """
        Get the categories of news articles from the specified website.

        Returns:
            None
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        categories = soup.find_all("a", class_="nw-o-link")
        # print first 15 categories
        for category in categories[:15]:
            print(category.text)
            # print the category link
            print(urljoin(self.url, category["href"]))
