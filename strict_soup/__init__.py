"""Extended version of BeautifulSoup with extra functions. WARNING: Modifies BeautifulSoup globally."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag


class StrictSelectError(Exception):
    """Exception raised when a strict_* function  fails to find a match."""


class StrictMixin(Tag):
    """Mixin for adding extra functions to BeautifulSoup objects."""

    # This is technically a type error because ResultSet[StrctTag] is not a subclass of ResultSet[Tag], but it
    # shouldn't cause any errors the way it's used.
    def select(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - These types are copied directly from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - These types are copied directly from the parent class
    ) -> ResultSet[StrictTag]:
        """.select that returns a ResultSet of StrctTag objects.

        Perform a CSS selection operation on the current element.

        This uses the SoupSieve library.

        :param selector: A string containing a CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
           used in the CSS selector to namespace URIs. By default,
           Beautiful Soup will use the prefixes it encountered while
           parsing the document.

        :param limit: After finding this number of results, stop looking.

        :param kwargs: Keyword arguments to be passed into SoupSieve's
           soupsieve.select() method.

        :return: A ResultSet of StrctTags.
        :rtype: bs4.element.ResultSet
        """
        output = super().select(selector, namespaces, limit, **kwargs)
        return ResultSet[StrictTag](output.source, [StrictTag(item) for item in output])

    def select_one(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - These types are copied directly from the parent class
        **kwargs: Any,  # noqa: ANN401 - These types are copied directly from the parent class
    ) -> StrictTag | None:
        """.select_one that returns a StrctTag object or None.

        :param selector: A CSS selector.

        :param namespaces: A dictionary mapping namespace prefixes
           used in the CSS selector to namespace URIs. By default,
           Beautiful Soup will use the prefixes it encountered while
           parsing the document.

        :param kwargs: Keyword arguments to be passed into Soup Sieve's
           soupsieve.select() method.

        :return: A StrctTag.
        :rtype: StrctTag
        """
        output = super().select_one(selector, namespaces, **kwargs)
        if output is None:
            return output

        return StrictTag(output)

    def strict_select(self, selector: str) -> ResultSet[StrictTag]:
        """.select with simplified parameters that will raise an exception if no matches are found."""
        output = self.select(selector)
        if len(output) == 0:
            msg = f"No matches found for strict_select({selector})"
            raise StrictSelectError(msg)

        return output

    def strict_select_one(self, selector: str) -> StrictTag:
        """.select_one with simplified parameters that will raise an exception if no matches are found."""
        output = self.strict_select(selector)
        if len(output) != 1:
            msg = f"Found {len(output)} matches for strict_select_one({selector})"
            raise StrictSelectError(msg)

        return output[0]

    def strict_get(self, key: str) -> str:
        """.get that will raise an exception if no matches are found."""
        output = self.get(key)
        if isinstance(output, str):
            return output

        msg = f"No matches found for strict_get({key})"
        raise StrictSelectError(msg)


class StrictTag(StrictMixin):
    """Tag object that has been extended with extra functions."""

    def __init__(self, tag: Tag | None) -> None:
        """Initialize the StrctTag object."""
        # Dynamically copy all attributes from the parent class to the child class
        parent_attributes = vars(tag)
        for attr_name, attr_value in parent_attributes.items():
            setattr(self, attr_name, attr_value)


class StrictSoup(BeautifulSoup, StrictMixin):  # type: ignore - This error is present in the original beautifulsoup
    # class because beautifulsoup is a subclass of Tag and beautifulsoup has a reportIncompatibleMethodOverride error in
    # the original code.
    """BeautifulSoup object that has been extended with extra functions."""
