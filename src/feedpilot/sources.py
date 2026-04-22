"""Default RSS/Atom feed sources for feedpilot."""

import tomllib
from importlib.resources import files


def _load_sources() -> list[dict]:
    data = files("feedpilot").joinpath("sources.toml").read_bytes()
    return tomllib.loads(data.decode())["sources"]


SOURCES: list[dict] = _load_sources()
