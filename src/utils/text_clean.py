import re

def clean_text(text: str) -> str:
    """
    Cleans text by removing URLs, emails, phone numbers, extra spaces, and special characters.
    """
    text = re.sub(r'https?://\S+|www\.\S+', '', text)          # Remove URLs
    text = re.sub(r'\S+@\S+', '', text)                        # Remove emails
    text = re.sub(r'\+?\d[\d\s-]{7,}\d', '', text)            # Remove phone numbers
    text = re.sub(r'[^a-zA-Z0-9\s.,;:!?()-]', '', text)       # Remove special chars
    text = re.sub(r'\n+', '\n', text)                          # Normalize newlines
    text = re.sub(r'\s+', ' ', text).strip()                  # Normalize spaces
    return text