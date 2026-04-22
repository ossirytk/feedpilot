"""Default RSS/Atom feed sources for feedpilot."""

import tomllib
from importlib.resources import files


def _load_sources() -> list[dict]:
    try:
        data = files("feedpilot").joinpath("sources.toml").read_bytes()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Could not load packaged feed source definitions from "
            "'feedpilot/sources.toml'. Ensure the file is included as package "
            "data in the built distribution."
        ) from exc

    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(
            "Invalid TOML in packaged feed source definitions "
            "('feedpilot/sources.toml')."
        ) from exc

    sources = parsed.get("sources")
    if not isinstance(sources, list):
        raise RuntimeError(
            "Packaged feed source definitions ('feedpilot/sources.toml') must "
            "define a top-level 'sources' list."
        )

    return sources
SOURCES: list[dict] = _load_sources()
