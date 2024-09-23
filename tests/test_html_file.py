"""Test the StrictSoup class."""

import pytest
from bs4 import BeautifulSoup

from src.strict_soup import StrictSelectError, StrictSoup

# For simplicity, the string should be on one line
PARSED_HTML = StrictSoup(
    """<h1 value="123"><text>H1 Test</text></h1>
    <h2><text>H2 Test 1</text></h2><h2>H2 Text 2</h2>""",
    "html.parser",
)

PARSED_BS4 = BeautifulSoup(
    """<h1 value="123"><text>H1 Test</text></h1>
    <h2><text>H2 Test 1</text></h2><h2>H2 Text 2</h2>""",
    "html.parser",
)


class TestBS4:
    # Make sure BS4 is not modified by the StrictSoup class
    def test_bs4_root_not_modified(self) -> None:
        assert not callable(getattr(PARSED_BS4, "strict_select", None))
        assert not callable(getattr(PARSED_BS4, "strict_select_one", None))
        assert not callable(getattr(PARSED_BS4, "strict_get", None))

    def test_bs4_tag_not_modified(self) -> None:
        h2 = PARSED_BS4.select_one("h2")
        assert not callable(getattr(h2, "strict_select", None))
        assert not callable(getattr(h2, "strict_select_one", None))
        assert not callable(getattr(h2, "strict_get", None))

class TestStrictSelect:
    def test_multiple_matches(self) -> None:
        result = PARSED_HTML.strict_select("h2")
        assert str(result) == "[<h2><text>H2 Test 1</text></h2>, <h2>H2 Text 2</h2>]"

    def test_single_match(self) -> None:
        result = PARSED_HTML.strict_select("h1")
        assert str(result) == '[<h1 value="123"><text>H1 Test</text></h1>]'

    def test_no_matches(self) -> None:
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")

    def test_child_matches(self) -> None:
        result = PARSED_HTML.strict_select("h2")[0].strict_select("text")
        assert str(result) == "[<text>H2 Test 1</text>]"


class TestStrictSelectOne:
    def test_single_match(self) -> None:
        assert (
            str(PARSED_HTML.strict_select_one("h1"))
            == '<h1 value="123"><text>H1 Test</text></h1>'
        )

    def test_no_matches(self) -> None:
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")

    def test_multiple_matches(self) -> None:
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h2")

    def test_child_matches(self) -> None:
        """Test that strict_select returns the correct value."""
        result = PARSED_HTML.strict_select("h2")[0].strict_select_one("text")
        assert str(result) == "<text>H2 Test 1</text>"


class TestStrictGet:
    def test_match(self) -> None:
        assert str(PARSED_HTML.strict_select_one("h1").strict_get("value")) == "123"

    def test_no_match(self) -> None:
        tag = PARSED_HTML.strict_select_one("h1")
        with pytest.raises(StrictSelectError):
            tag.strict_get("missing_value")
