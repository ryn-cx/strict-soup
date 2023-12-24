"""Tests for the StrangeStew class."""
import pytest

from strict_soup import StrictSelectError, StrictSoup

PARSED_HTML = StrictSoup('<h1 value="123">Test</h1><h2>Test</h2><h2>Test</h2>')


class TestStrictSelect:
    """Tests for the strict_select function."""

    def test_strict_select(self) -> None:
        """Test that strict_select returns the correct value."""
        assert str(PARSED_HTML.strict_select("h2")) == "[<h2>Test</h2>, <h2>Test</h2>]"

    def test_strict_select_failure(self) -> None:
        """Test that strict_select raises an exception when no matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")


class TestStrictSelectOne:
    """Tests for the strict_select_one function."""

    def test_success(self) -> None:
        """Test that strict_select_one returns the correct value."""
        assert str(PARSED_HTML.strict_select_one("h1")) == '<h1 value="123">Test</h1>'

    def test_failure_no_values(self) -> None:
        """Test that strict_select_one raises an exception when no matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h3")

    def test_failure_too_many_values(self) -> None:
        """Test that strict_select_one raises an exception when too many matches are found."""
        with pytest.raises(StrictSelectError):
            PARSED_HTML.strict_select_one("h2")


class TestStrictGet:
    """Tests for the strict_get function."""

    def test_success(self) -> None:
        """Test that strict_get returns the correct value."""
        assert str(PARSED_HTML.strict_select_one("h1").strict_get("value")) == "123"

    def test_failure(self) -> None:
        """Test that strict_get raises an exception when no matches are found."""
        tag = PARSED_HTML.strict_select_one("h1")
        with pytest.raises(StrictSelectError):
            tag.strict_get("missing_value")
