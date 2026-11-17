"""
Visual-First Story Slicer & Illustration Extractor.
Extracts illustrations and chapters from EPUB, PDF, and TXT storybooks,
generating rich, graphics-driven 60-second video compositions.
"""

import json
import os
import re
import zipfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = BASE_DIR / "books"
HISTORY_FILE = BASE_DIR / "story_pipeline" / "story_history.json"
PUBLIC_IMAGES_DIR = BASE_DIR / "video-app" / "public" / "images"


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"processed_chapters": [], "last_book": None, "episode_count": 0}


def save_history(history: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def extract_epub_illustrations(epub_path: Path) -> dict:
    """Extracts all embedded media images to public/images and returns a mapping."""
    PUBLIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    extracted = {}

    with zipfile.ZipFile(str(epub_path), "r") as z:
        for name in z.namelist():
            lower = name.lower()
            if any(lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".svg"]):
                filename = Path(name).name
                data = z.read(name)
                out_file = PUBLIC_IMAGES_DIR / filename
                out_file.write_bytes(data)
                extracted[filename] = f"images/{filename}"

    return extracted


def read_epub_stories(file_path: Path) -> list[dict]:
    """Extracts chapters and links them to their high-res illustrations."""
    image_map = extract_epub_illustrations(file_path)
    from bs4 import BeautifulSoup

    scenes = []
    with zipfile.ZipFile(str(file_path), "r") as z:
        ch_files = [
            f for f in z.namelist()
            if f.lower().endswith((".xhtml", ".html", ".htm"))
            and not any(x in f.lower() for x in ["nav.", "toc.", "copyright", "title_page"])
        ]
        ch_files.sort()

        for ch_name in ch_files:
            try:
                content = z.read(ch_name).decode("utf-8", errors="ignore")
                soup = BeautifulSoup(content, "html.parser")

                # Find associated image
                img_tag = soup.find("img")
                img_filename = Path(img_tag.get("src")).name if img_tag else None
                image_rel_path = image_map.get(img_filename) if img_filename else None

                # Clean text
                for tag in soup(["script", "style", "nav"]):
                    tag.decompose()

                header = soup.find(["h1", "h2", "h3"])
                title = header.get_text().strip() if header else None

                text = soup.get_text(separator=" ", strip=True)
                # Strip repetitive filename or boilerplate
                base_name = Path(ch_name).name
                text = text.replace(base_name, "").strip()

                if len(text) < 20 and not image_rel_path:
                    continue

                clean_title = title or f"Scene {len(scenes) + 1}"
                # If title is in text, clean up text
                if title and text.startswith(title):
                    text = text[len(title) :].strip()
                if title and text.startswith(title):
                    text = text[len(title) :].strip()

                scenes.append({
                    "title": clean_title,
                    "text": text or clean_title,
                    "image_url": image_rel_path,
                })
            except Exception as e:
                print(f"Notice: skipped {ch_name} ({e})")

    # Bundle scenes into episodic 60-second video groups (3-4 scenes per episode)
    episodes = []
    scenes_per_ep = 4
    for i in range(0, len(scenes), scenes_per_ep):
        ep_scenes = scenes[i : i + scenes_per_ep]
        first_title = ep_scenes[0]["title"]
        ep_num = len(episodes) + 1
        episodes.append({
            "title": f"Episode {ep_num}: {first_title}",
            "scenes": ep_scenes,
        })

    return episodes


def read_pdf_stories(file_path: Path) -> list[dict]:
    """Reads PDF and groups into story episodes."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n\n".join(pages)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        full_text = ""

    episodes = []
    words = full_text.split()
    chunk_size = 200
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk.strip()) > 80:
            episodes.append({
                "title": f"Episode {len(episodes) + 1}",
                "scenes": [{"title": f"Part {len(episodes) + 1}", "text": chunk, "image_url": None}],
            })
    return episodes


def extract_next_story_slice() -> dict | None:
    """Finds the next unprocessed story episode from the books/ folder."""
    books = (
        list(BOOKS_DIR.glob("*.epub"))
        + list(BOOKS_DIR.glob("*.EPUB"))
        + list(BOOKS_DIR.glob("*.pdf"))
        + list(BOOKS_DIR.glob("*.txt"))
    )

    if not books:
        print(f"No books found in '{BOOKS_DIR}'. Place a .epub or .pdf storybook there.")
        return None

    history = load_history()
    processed = set(history.get("processed_chapters", []))

    for book in books:
        if book.suffix.lower() == ".epub":
            episodes = read_epub_stories(book)
        elif book.suffix.lower() == ".pdf":
            episodes = read_pdf_stories(book)
        else:
            text = book.read_text(encoding="utf-8", errors="ignore")
            episodes = [{"title": "Story Episode", "scenes": [{"title": "Story", "text": text, "image_url": None}]}]

        for idx, ep in enumerate(episodes):
            ep_id = f"{book.name}::{ep['title']}"
            if ep_id not in processed:
                return {
                    "book_name": book.name,
                    "episode_title": ep["title"],
                    "episode_id": ep_id,
                    "scenes_raw": ep["scenes"],
                    "episode_number": history.get("episode_count", 0) + 1,
                }

    print("All episodes from existing books have been processed! Ready for a new book.")
    return None


def generate_video_script(story_slice: dict) -> dict:
    """Creates a visual-first 60-second video script with illustrations and kinetic captions."""
    book_name = story_slice["book_name"]
    ep_title = story_slice["episode_title"]
    ep_num = story_slice["episode_number"]
    scenes_raw = story_slice["scenes_raw"]

    clean_book_name = (
        book_name.replace(".epub", "")
        .replace(".pdf", "")
        .replace(".txt", "")
        .replace("Various_", "")
        .replace("_", " ")
    )

    formatted_scenes = []
    spoken_sentences = []

    for i, s in enumerate(scenes_raw):
        text = s["text"].strip()
        img = s.get("image_url")
        title = s.get("title", f"Scene {i + 1}")

        # Choose a punchy highlight phrase
        words = text.split()
        highlight = " ".join(words[:4]) if len(words) >= 4 else text

        formatted_scenes.append({
            "scene_number": i + 1,
            "title": title,
            "narration": text,
            "highlight_phrase": highlight,
            "image_url": img,  # The high-res illustration!
            "bg_gradient": "radial-gradient(ellipse at center, #1e1b4b 0%, #060515 100%)",
            "emoji": "🦁" if "lion" in clean_book_name.lower() else "✨",
        })
        spoken_sentences.append(text)

    full_narration = " ".join(spoken_sentences)

    # Determine music mood
    genre = "Children Adventure / Warm" if "lion" in clean_book_name.lower() else "Fantasy / Story"

    return {
        "book_title": clean_book_name,
        "chapter_title": ep_title,
        "episode": ep_num,
        "genre": genre,
        "hook": ep_title.upper()[:28],
        "full_narration": full_narration,
        "scenes": formatted_scenes,
    }
