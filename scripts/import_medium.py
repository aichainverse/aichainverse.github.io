#!/usr/bin/env python3
"""Turn the Medium article folders into English blog posts for this site.

Each folder (NN-slug/) holds article.html, publish.md and the article's images. For every entry in
ARTICLES below this writes _posts/en/<date>-<slug>.html and copies the images to assets/img/blog/<slug>/
(PNG files are converted to JPEG so pages stay light).

Run from the repo root:

    uv run --with pillow scripts/import_medium.py /path/to/projects/medium [/path/to/Downloads]

The optional second folder is where extra covers (`cover`, `shorts_dir` below) are looked up. Without it,
the copies already in assets/img/blog/ are reused.

Re-running overwrites the generated posts, so make text changes in the Medium source (or stop
re-importing that article by removing it from ARTICLES).
"""
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts" / "en"
IMAGES = ROOT / "assets" / "img" / "blog"
MAX_WIDTH = 1600
EXTRAS = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/nonexistent")

# folder -> publish date (site timezone) and the links that fill that article's [LINK: ...] placeholders.
# A placeholder with no link here loses its link (the words stay), or its line if it sat on its own line.
# `caption_links` (image file name without extension -> URL) turns that image's caption into a link.
# `cover` (image file in the Downloads folder, alt text) gives an article a cover that its Medium version doesn't have; once copied
# into the site it is reused from there if the original file is gone.
# `shorts` lists the article's YouTube Shorts, shown as cards under the article; their covers are copied from
# `shorts_dir` when that folder is present (otherwise the copies already in the site, or YouTube's own, are used).
ARTICLES = {
    "01-how-ai-sees-a-photo": {"date": "2026-11-05 09:00:00 +0500", "caption_links": {
        "cnn-infographic": "https://www.facebook.com/photo.php?fbid=122121994815487843",
    }, "shorts_dir": "aichainverse-shorts-cnn", "shorts": [
        # (YouTube id, title, cover file in the Downloads sub-folder `shorts_dir`), in posting order
        ("kGSLZByNNug", "A Tiny Pattern Turned a Panda Into a Gibbon", "aichainverse-short-cnn-01-panda-gibbon-thumbnail-1080x1920.png"),
        ("WYGPofMBtMA", "3 Myths About How AI Sees Images", "aichainverse-short-cnn-02-myths-thumbnail-1080x1920.png"),
        ("GL9PSFTReTA", "To AI, Your Photo Is Just 3 Million Numbers", "aichainverse-short-cnn-04-photo-numbers-thumbnail-1080x1920.png"),
        ("gxjaZ-B9SzI", "The 2012 Contest That Started the AI Boom", "aichainverse-short-cnn-03-alexnet-thumbnail-1080x1920.png"),
        ("z39u5nzcw6k", "Nobody Trains Image AI From Scratch Anymore", "aichainverse-short-cnn-06-transfer-learning-thumbnail-1080x1920.png"),
        ("-sNh4hdpQ78", "How Your Phone Finds Your Cat in One Second", "aichainverse-short-cnn-05-whole-journey-thumbnail-1080x1920.png"),
    ]},
    "02-how-chatgpt-writes": {"date": "2026-11-05 10:00:00 +0500", "cover": (
        "aichainverse-youtube-llm-thumbnail-1280x720.png",
        "AIChainVerse cover: How ChatGPT writes. LLMs, Large Language Models. Guess, add, repeat."),
        "shorts_dir": "aichainverse-shorts-llm", "shorts": [
        ("mPxDWZYC5jU", "Lawyers Fined $5,000 Over Fake ChatGPT Cases", "aichainverse-short-llm-01-hallucination-thumbnail-1080x1920.png"),
        ("J6bSrmiCuLg", "3 Myths About ChatGPT (Most People Believe #2)", "aichainverse-short-llm-02-myths-thumbnail-1080x1920.png"),
        ("guQPcePtUec", "How ChatGPT Picks the Next Word", "aichainverse-short-llm-03-next-token-guess-thumbnail-1080x1920.png"),
        ("z-dVBwn1zLs", "What Is an LLM? Explained in One Sentence", "aichainverse-short-llm-04-llm-one-sentence-thumbnail-1080x1920.png"),
        ("UQ2IoHOn3cY", "Why ChatGPT Gives Different Answers Every Time", "aichainverse-short-llm-05-temperature-thumbnail-1080x1920.png"),
    ]},
    "03-what-is-an-ai-agent": {"date": "2026-11-07 09:00:00 +0500", "links": {
        "YouTube link": "https://www.youtube.com/watch?v=JHo6qXs16MY",
    }},
    "04-why-perfect-models-fail": {"date": "2026-11-08 09:00:00 +0500"},
    "05-your-crypto-wallet-holds-zero-crypto": {"date": "2026-11-09 09:00:00 +0500", "links": {
        "crypto wallet explainer video": "https://www.youtube.com/watch?v=vsQ5_1qqY7A",
        "gas fees explainer": "https://www.youtube.com/watch?v=VKSpfYWSibc",
        "Seed Phrase Short": "https://www.youtube.com/shorts/OLAZEiwc7eY",
        "stablecoins explainer": "https://www.youtube.com/watch?v=m1_gWOlfqYs",
        "blockchain node explainer": "https://www.youtube.com/watch?v=qjH414kFYS0",
        "Facebook post #67": "https://www.facebook.com/photo.php?fbid=122118259917487843",
    }},
    "06-who-checks-a-bitcoin-payment": {"date": "2026-11-11 09:00:00 +0500"},
    "07-nobody-hacked-the-blockchain": {"date": "2026-11-12 09:00:00 +0500"},
}

# Links to the Medium copy of an article point at the copy on this site instead.
MEDIUM_TO_FOLDER = {
    "your-crypto-wallet-holds-zero-crypto-cf44c00861bf": "05-your-crypto-wallet-holds-zero-crypto",
    "who-checks-a-bitcoin-payment-when-theres-no-bank-ff59f7aeda4b": "06-who-checks-a-bitcoin-payment",
}

YOUTUBE = re.compile(r"https://(?:www\.)?(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([\w-]{11})")
unresolved = []


def slug_of(folder):
    return folder.split("-", 1)[1]


def post_url(folder):
    y, m, d = ARTICLES[folder]["date"].split(" ")[0].split("-")
    return f"/blog/{y}/{m}/{d}/{slug_of(folder)}/"


def find_link(label, links):
    """Match a placeholder label such as 'stablecoins explainer video' to a key in `links`."""
    label = label.lower()
    for key, url in links.items():
        if key.lower() in label or label in key.lower():
            return url
    return None


def embed(video_id):
    return (f'<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
            'title="YouTube video" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; '
            'gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>')


def copy_image(src, slug, max_width=MAX_WIDTH):
    """Copy one image into the site (PNG -> JPEG, capped at max_width). Returns (url, width, height)."""
    out_dir = IMAGES / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        if im.width > max_width:
            im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
        out = out_dir / (src.stem + ".jpg")
        if src.suffix.lower() == ".png" or im.width == max_width:
            im.convert("RGB").save(out, "JPEG", quality=85, optimize=True, progressive=True)
        else:
            out.write_bytes(src.read_bytes())
        return f"/assets/img/blog/{slug}/{out.name}", im.width, im.height


def yaml_str(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def unescape(text):
    return text.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">")


def convert(source, folder):
    cfg = ARTICLES[folder]
    links = cfg.get("links", {})
    slug = slug_of(folder)
    src_dir = source / folder
    html = (src_dir / "article.html").read_text(encoding="utf-8")
    body = re.search(r"<body>(.*)</body>", html, re.S).group(1)

    # Medium-only parts: the copy/paste instructions, and the title and subtitle (the layout prints those).
    body = re.sub(r'<div class="help">.*?</div>', "", body, count=1, flags=re.S)
    title = unescape(re.search(r"<h1>(.*?)</h1>", body, re.S).group(1).strip())
    body = re.sub(r"<h1>.*?</h1>", "", body, count=1, flags=re.S)
    description = unescape(re.search(r'<p class="subtitle">(.*?)</p>', body, re.S).group(1).strip())
    body = re.sub(r'<p class="subtitle">.*?</p>', "", body, count=1, flags=re.S)

    # Link placeholders. On their own line they are a video to embed; inline they wrap the linked words.
    def own_line(match):
        label = re.sub(r"\[LINK:|\]", "", re.sub(r"<[^>]+>", "", match.group(0))).strip()
        url = find_link(label, links)
        if url and YOUTUBE.match(url):
            return f"<p>{url}</p>"
        unresolved.append(f"{folder}: no video for '{label}' (embed left out)")
        return ""
    body = re.sub(r'<p class="todo">.*?</p>|<p><span class="todo">.*?</span></p>', own_line, body, flags=re.S)

    def inline(match):
        label, words = match.group(1).strip(), match.group(2).strip()
        url = find_link(label, links)
        if url:
            return f'<a href="{url}">{words}</a>'
        unresolved.append(f"{folder}: no link for '{label}' (\"{words}\" left as plain text)")
        return words
    body = re.sub(r'<a href="#"><span class="todo">\[LINK:(.*?)\]</span>(.*?)</a>', inline, body, flags=re.S)

    def bare(match):
        # A placeholder followed by the words it belongs to ("[YouTube link]: watch the full video ... on").
        label, words = match.group(1).strip(), match.group(2)
        words = words[:1].upper() + words[1:]
        url = find_link(label, links)
        if url:
            return f'<a href="{url}">{words}</a>'
        unresolved.append(f"{folder}: no link for '{label}' (placeholder removed)")
        return words
    body = re.sub(r'<span class="todo">(.*?)</span>:?\s*([^<]*?)(?= on <a|[.<])', bare, body, flags=re.S)

    # A YouTube URL alone in a paragraph becomes an embedded player.
    body = re.sub(r"<p>\s*(?:<a [^>]*>)?\s*" + YOUTUBE.pattern + r"[^<\s]*\s*(?:</a>)?\s*</p>",
                  lambda m: embed(m.group(1)), body)

    for medium_id, target in MEDIUM_TO_FOLDER.items():
        body = re.sub(r'https://medium\.com/@[\w.-]+/' + re.escape(medium_id), post_url(target), body)

    # Images: copy into the site and point at the copy. An image that opens the article is the cover,
    # which the layout prints; otherwise the first image doubles as the card and sharing picture.
    cover = {}
    opens_with_image = body.lstrip().startswith("<figure>")

    def image(match):
        tag = match.group(0)
        name = re.search(r'src="([^"]+)"', tag).group(1)
        alt = re.search(r'alt="([^"]*)"', tag)
        alt = alt.group(1) if alt else ""
        url, width, height = copy_image(src_dir / name, slug)
        if not cover:
            cover.update(url=url, alt=unescape(alt))
        return f'<img src="{url}" alt="{alt}" width="{width}" height="{height}" loading="lazy">'
    body = re.sub(r"<img\b[^>]*>", image, body)
    for name, url in cfg.get("caption_links", {}).items():
        body, hits = re.subn(r'(<img src="[^"]*/' + re.escape(name) + r'\.jpg"[^>]*>\s*<figcaption>)(.*?)(</figcaption>)',
                             lambda m: f'{m.group(1)}<a href="{url}">{m.group(2)}</a>{m.group(3)}', body, flags=re.S)
        if not hits:
            unresolved.append(f"{folder}: no caption found under image '{name}'")

    if opens_with_image:
        body = re.sub(r"<figure>\s*<img\b[^>]*>\s*</figure>", "", body, count=1)

    if cfg.get("cover"):
        src, alt = EXTRAS / cfg["cover"][0], cfg["cover"][1]
        copied = IMAGES / slug / (src.stem + ".jpg")
        if src.is_file():
            cover.update(url=copy_image(src, slug)[0], alt=alt)
            opens_with_image = True
        elif copied.is_file():
            cover.update(url=f"/assets/img/blog/{slug}/{copied.name}", alt=alt)
            opens_with_image = True
        else:
            unresolved.append(f"{folder}: cover file not found: {src}")

    if "{{" in body or "{%" in body:
        raise SystemExit(f"{folder}: contains Liquid-like braces; wrap them in {{% raw %}} first")

    publish = (src_dir / "publish.md").read_text(encoding="utf-8")
    tags = re.search(r"\*\*Tags[^*]*\*\*\s*(.+)", publish)
    tags = [t.strip() for t in tags.group(1).split(",")] if tags else []

    front = ["---", f"title: {yaml_str(title)}", f"description: {yaml_str(description)}", f"date: {cfg['date']}"]
    if cover:
        front += [f"image: {cover['url']}", f"image_alt: {yaml_str(cover['alt'])}"]
        if not opens_with_image:
            front.append("cover: false   # the image appears inside the article, so it is not repeated on top")
    if tags:
        front.append("tags: [" + ", ".join(yaml_str(t) for t in tags) + "]")
    if cfg.get("shorts"):
        front.append("shorts:")
        for video_id, short_title, cover_file in cfg["shorts"]:
            src = EXTRAS / cfg.get("shorts_dir", "") / cover_file
            copied = IMAGES / slug / (Path(cover_file).stem + ".jpg")
            if src.is_file():
                thumb = copy_image(src, slug, max_width=540)[0]
            elif copied.is_file():
                thumb = f"/assets/img/blog/{slug}/{copied.name}"
            else:
                thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            front.append(f"  - {{ youtube_id: {yaml_str(video_id)}, title: {yaml_str(short_title)}, image: {thumb} }}")
    front.append("---")

    POSTS.mkdir(parents=True, exist_ok=True)
    out = POSTS / f"{cfg['date'].split(' ')[0]}-{slug}.html"
    out.write_text("\n".join(front) + "\n" + re.sub(r"\n{3,}", "\n\n", body).strip() + "\n", encoding="utf-8")
    print(f"{out.relative_to(ROOT)}  ->  {post_url(folder)}")


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    source = Path(sys.argv[1])
    for folder in ARTICLES:
        convert(source, folder)
    if unresolved:
        print("\nMissing links (add them to ARTICLES and re-run):")
        for line in unresolved:
            print("  -", line)


if __name__ == "__main__":
    main()
