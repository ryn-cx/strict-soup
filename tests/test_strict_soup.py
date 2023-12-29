"""Tests for the StrangeStew class."""
import pytest

from strict_soup import StrictSelectError, StrictSoup

PARSED_HTML = StrictSoup(
    '<h1 value="123"><text>H1 Test</text></h1><h2><text>H2 Test 1</text></h2><h2>H2 Text 2</h2>',
    "html.parser",
)


class TestStrictSelect:
    """Tests for the strict_select function."""

    def test_multiple_matches(self) -> None:
        """Test that strict_select returns the correct value."""
        result = PARSED_HTML.strict_select("h2")
        assert str(result) == "[<h2><text>H2 Test 1</text></h2>, <h2>H2 Text 2</h2>]"

    def test_single_match(self) -> None:
        """Test that strict_select returns the correct value."""
        result = PARSED_HTML.strict_select("h1")
        assert str(result) == '[<h1 value="123"><text>H1 Test</text></h1>]'

    def test_no_matches(self) -> None:
        """Test that strict_select raises an exception when no matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")

    def test_child_matches(self) -> None:
        """Test that strict_select returns the correct value."""
        result = PARSED_HTML.strict_select("h2")[0].strict_select("text")
        assert str(result) == "[<text>H2 Test 1</text>]"


class TestStrictSelectOne:
    """Tests for the strict_select_one function."""

    def testsingle_match(self) -> None:
        """Test that strict_select_one returns the correct value."""
        assert str(PARSED_HTML.strict_select_one("h1")) == '<h1 value="123"><text>H1 Test</text></h1>'

    def test_no_matces(self) -> None:
        """Test that strict_select_one raises an exception when no matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")

    def test_multiple_matches(self) -> None:
        """Test that strict_select_one raises an exception when too many matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h2")

    def test_child_matches(self) -> None:
        """Test that strict_select returns the correct value."""
        result = PARSED_HTML.strict_select("h2")[0].strict_select_one("text")
        assert str(result) == "<text>H2 Test 1</text>"


class TestStrictGet:
    """Tests for the strict_get function."""

    def test_match(self) -> None:
        """Test that strict_get returns the correct value."""
        assert str(PARSED_HTML.strict_select_one("h1").strict_get("value")) == "123"

    def test_no_match(self) -> None:
        """Test that strict_get raises an exception when no matches are found."""
        tag = PARSED_HTML.strict_select_one("h1")
        with pytest.raises(StrictSelectError):
            tag.strict_get("missing_value")
