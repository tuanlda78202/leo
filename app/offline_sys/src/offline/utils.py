import random
import string

import tiktoken
from loguru import logger


def generate_random_hex(length: int) -> str:
    # Generate a random string of the specified length using hexadecimal characters for NotionDoc ID.
    hex_chars = string.hexdigits.lower()
    return "".join(random.choice(hex_chars) for _ in range(length))


def clip_tokens(text: str, max_tokens: int, model_id: str) -> str:
    """Clip the text to a maximum number of tokens using the tiktoken tokenizer.

    Args:
        text: The input text to clip.
        max_tokens: Maximum number of tokens to keep (default: 8192).
        model_id: The model name to determine encoding (default: "gpt-4").

    Returns:
        str: The clipped text that fits within the token limit.
    """

    try:
        encoding = tiktoken.encoding_for_model(
            model_id
        )  # TODO: not compatible with gemini models
    except KeyError:
        # Fallback to cl100k_base encoding (used by gpt-4, gpt-3.5-turbo, text-embedding-ada-002)
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text

    return encoding.decode(tokens[:max_tokens])
