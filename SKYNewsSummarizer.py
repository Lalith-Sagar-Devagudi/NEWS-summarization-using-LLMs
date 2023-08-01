"""
This module provides a SKYNewsSummarizer class for scraping and summarizing news articles from a specified website.

Author: Lalith Sagar, Devagudi
Date: July 23, 2023
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
from summarize import summarize
from Article import Article


class SKYNewsSummarizer:
    """
    SKYNewsSummarizer class for scraping and summarizing news articles.

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
            category (str): The category of news articles to scrape (optional).
            body (bool): Whether to include the full article body or not.
            summarized (bool): Whether to summarize the articles or not.

        Returns:
            None
        """
        # Handle category-specific scraping
        if category:
            self.url = self.url + "/" + category.lower()
        else:
            self.url = self.url + "/"

        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        container = soup.find("div", class_="sdc-site-tiles__group")

        # Scraping articles from the selected container
        for article in container.find_all("div", class_="sdc-site-tile"):
            title = article.find("h3", class_="sdc-site-tile__headline").text.strip()
            link = urljoin(
                self.url,
                article.find("a", class_="sdc-site-tile__headline-link")["href"],
            )

            # Add the article to the list if the title is unique
            if title not in self.seen_titles:
                self.articles.append(
                    {
                        "title": title,
                        "link": link,
                    }
                )
                self.seen_titles.add(title)

        # Printing the scraped articles
        print("Number of articles:", len(self.articles))
        for article in self.articles:
            print("Title:", article["title"])
            print("Link:", article["link"])
            inside_article = requests.get(article["link"])
            inside_soup = BeautifulSoup(inside_article.content, "html.parser")
            parsed_article = Article(inside_soup)
            print("Inside Link Title:", parsed_article.title)
            # If body is requested and summarization is not needed
            if body and not summarized:
                body_text = " ".join(
                    parsed_article.get_body(
                        body_divs=inside_soup.find_all("div", {"class": "content"})
                    )
                )
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
        categories = soup.find_all("a", class_="ui-news-header-nav-items-link")
        for category in categories[:15]:
            print(category.text)
            print(urljoin(self.url, category["href"]))
