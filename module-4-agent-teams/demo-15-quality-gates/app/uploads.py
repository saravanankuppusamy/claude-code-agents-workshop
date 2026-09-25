"""Author photo uploads."""
import os

UPLOAD_DIR = "static/authors"


def save_photo(filename, data):
    path = os.path.join(UPLOAD_DIR, filename)      # ../../ path traversal
    with open(path, "wb") as f:
        f.write(data)
    return path
