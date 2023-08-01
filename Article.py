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
        soup (BeautifulSoup): The BeautifulSoup object for parsing HTML content.
        body (list): List of paragraphs constituting the article body.
        title (str): The title of the article.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup object.
    """

    def __init__(self, soup: BeautifulSoup):
        """
        Initialize an article.

        Args:
            url (str): The URL of the article.
        """
        self.soup = soup
        self.body = self.get_body(body_divs=None)
        self.title = self.get_title()

    def get_body(
        self,
        body_divs: list = None,
    ) -> list:
        """
        Extract paragraphs constituting the article body.

        Parameters:
            body_divs (list): List of divs containing the article body.

        Returns:
            list: List of paragraphs constituting the article body.
        """
        if not body_divs:
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
