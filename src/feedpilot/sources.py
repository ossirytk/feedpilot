"""Default RSS/Atom feed sources for feedpilot."""

import tomllib
from importlib.resources import files


def _load_sources() -> list[dict]:
    try:
        data = files("feedpilot").joinpath("sources.toml").read_bytes()
    except FileNotFoundError as exc:
        msg = (
            "Could not load packaged feed source definitions from "
            "'feedpilot/sources.toml'. Ensure the file is included as package "
            "data in the built distribution."
        )
        raise RuntimeError(msg) from exc

    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        msg = "Invalid TOML in packaged feed source definitions ('feedpilot/sources.toml')."
        raise RuntimeError(msg) from exc

    sources = parsed.get("sources")
    if not isinstance(sources, list):
        msg = "Packaged feed source definitions ('feedpilot/sources.toml') must define a top-level 'sources' list."
        raise TypeError(msg)

    return sources


SOURCES: list[dict] = _load_sources()
