"""
This file contains summarization functions using OpenAI models.

Author: Lalith Sagar, Devagudi
Date: July 22, 2023
"""

import openai


def summarize(body: str, api_key: str):
    """
    Summarizes the given text using the OpenAI GPT-3 model.

    Args:
        body (str): The text to be summarized.
        api_key (str): The OpenAI API key for authentication.

    Returns:
        None
    """
    # Set up your OpenAI API credentials
    openai.api_key = api_key
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
