import re

from typing import Optional
from urllib.parse import urlparse
from urlextract import URLExtract


def is_valid_url(url: str) -> bool:
    try:
        parsed_url = urlparse(url)
        return bool(all([parsed_url.scheme, parsed_url.netloc]))
    except ValueError:
        return False


def convert_urls_to_links(text: str, extractor: Optional[URLExtract] = None) -> str:
    if extractor is None:
        extractor = URLExtract()

    offset = 0
    urls = extractor.find_urls(text, get_indices=True)
    
    for url, indices in urls:
        if not is_valid_url(url):
            continue

        start_idx, end_idx = indices
        offset_start_idx = start_idx + offset
        offset_end_idx = end_idx + offset
        
        safe_url = url.strip(" .,").replace(" ", "")
        href = safe_url if url.startswith(("http://", "https://")) else f"https://{safe_url}"
        link_html = f'<a href="{href}">{safe_url}</a>'
        text = text[:offset_start_idx] + link_html + text[offset_end_idx:]
        offset += len(link_html) - len(url)

    return text


def fix_hyphenation(text: str) -> str:
    pattern = r'(\w+)-\s+(\w+)'
    return re.sub(pattern, lambda m: m.group(1) + m.group(2), text)