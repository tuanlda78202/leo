import random
import string


def generate_random_hex(length: int) -> str:
    # Generate a random string of the specified length using hexadecimal characters for NotionDoc ID.
    hex_chars = string.hexdigits.lower()
    return "".join(random.choice(hex_chars) for _ in range(length))
