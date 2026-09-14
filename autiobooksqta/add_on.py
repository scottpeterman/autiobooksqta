import io

import ebooklib
from PyQt6.QtCore import QEvent

from autiobooksqta.engine_pyqt import get_title, get_author, resized_image


def get_cover_from_open_library(title, author):
    """Try to get a book cover from Open Library API based on title and author"""
    import requests
    import urllib.parse

    # Clean and encode search terms
    query = urllib.parse.quote(f"{title} {author}")

    try:
        # Search Open Library for matching books
        search_url = f"https://openlibrary.org/search.json?q={query}"
        response = requests.get(search_url, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Check if we got any results
            if data.get('docs') and len(data['docs']) > 0:
                # Get the first result's OLID (Open Library ID)
                olid = data['docs'][0].get('key', '').replace('/works/', '')

                if olid:
                    # Get cover image using OLID
                    cover_url = f"https://covers.openlibrary.org/b/olid/{olid}-L.jpg"
                    img_response = requests.get(cover_url, timeout=5)

                    # Check if we got an actual image (not the default image)
                    if img_response.status_code == 200 and len(img_response.content) > 1000:
                        return img_response.content

        return None
    except Exception as e:
        print(f"Error fetching cover from Open Library: {e}")
        return None


class StatusUpdateEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, status_message, progress_message, chapter_id=None):
        super().__init__(StatusUpdateEvent.EVENT_TYPE)
        self.status_message = status_message
        self.progress_message = progress_message if progress_message else status_message
        self.chapter_id = chapter_id

def get_cover_image(book, resized):
    # Try to get cover from epub file first
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_COVER:
            if resized:
                return resized_image(item)
            else:
                return item.get_content()
        if item.get_type() == ebooklib.ITEM_IMAGE:
            if 'cover' in item.get_name().lower():
                if resized:
                    return resized_image(item)
                else:
                    return item.get_content()

    # If no cover was found in the epub, try Open Library
    try:
        title = get_title(book)
        author = get_author(book)
        if title:
            cover_data = get_cover_from_open_library(title, author)
            if cover_data:
                if resized:
                    # Create a temporary file-like object to load the image
                    img_bytes = io.BytesIO(cover_data)
                    temp_item = type('', (), {})()  # Create a simple object
                    temp_item.get_content = lambda: cover_data
                    return resized_image(temp_item)
                else:
                    return cover_data
    except Exception as e:
        print(f"Error using Open Library fallback: {e}")

    return None