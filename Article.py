"""
This module defines the `Article` class for representing an article.

Author: Lalith Sagar, Devagudi
Date: July 22, 2023
"""

import requests
from bs4 import BeautifulSoup


class Article:
    """
    Represents an article.

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
            url (str): The URL of the article.
        """
        article = requests.get(url)
        self.soup = BeautifulSoup(article.content, "html.parser")
        self.body = self.get_body()
        self.title = self.get_title()

    def get_body(self) -> list:
        """
        Extract paragraphs constituting the article body.

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
