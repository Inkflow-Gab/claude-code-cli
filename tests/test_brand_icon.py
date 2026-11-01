"""The Nullx11 Code mark stays standalone and does not depend on fonts or URLs."""

from pathlib import Path
from xml.etree import ElementTree

ICON = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "free_claude_code"
    / "assets"
    / "app-icon.svg"
)


def test_app_icon_is_own_two_tone_vector() -> None:
    source = ICON.read_text(encoding="utf-8")
    root = ElementTree.fromstring(source)
    assert root.attrib["viewBox"] == "0 0 1024 1024"
    assert root.attrib["aria-label"] == "Nullx11 Code icon"
    assert len(root.findall(".//{http://www.w3.org/2000/svg}linearGradient")) >= 2
    assert "#f97316" not in source  # Old orange FCC icon.
    assert "href=" not in source and "<text" not in source
