"""Default RSS/Atom feed sources for feedpilot."""

SOURCES: list[dict] = [
    {
        "name": "Phoronix",
        "url": "https://www.phoronix.com/rss.php",
        "tags": ["linux", "hardware", "benchmarks"],
    },
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
        "tags": ["tech", "programming"],
    },
    {
        "name": "LWN.net",
        "url": "https://lwn.net/headlines/rss",
        "tags": ["linux", "kernel"],
    },
    {
        "name": "GitHub Blog",
        "url": "https://github.blog/feed/",
        "tags": ["github", "devtools"],
    },
]
