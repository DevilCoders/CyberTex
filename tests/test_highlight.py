from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sapl.highlight import RESET, highlight_source


def test_highlight_adds_colour_sequences():
    source = 'SET host = "example"\n'
    result = highlight_source(source, theme="dark")
    assert "SET" in result
    assert "example" in result
    assert "\033[38;5;81mSET" in result
    assert result.endswith(RESET)
