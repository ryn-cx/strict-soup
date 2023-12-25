"""Extended version of BeautifulSoup with extra functions. WARNING: Modifies BeautifulSoup globally."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag


class StrictSelectError(Exception):
    """Exception raised when a strict_* function fails to find a match."""


class StrictMixin(Tag):
    """Mixin for adding extra functions to BeautifulSoup objects."""

    # This is technically a type error because ResultSet[StrctTag] is not a subclass of ResultSet[Tag], but it
    # shouldn't cause any errors the way it's used.
    def select(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - This type is copied directly from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - This type is copied directly from the parent class
    ) -> ResultSet[StrictTag]:
        """.select_one that returns a StrctTag object or None if no match is found.

        Args:
        ----
            selector: The string used to select elements from the source.
            namespaces: The namespaces to use when selecting elements.
            limit: The maximum number of elements to return. If None, all matching elements are returned.
            **kwargs: Additional arguments to pass to the parent class's select method.

        Returns:
        -------
            A ResultSet containing the selected elements, each wrapped in a StrictTag object.
        """
        output = super().select(selector, namespaces, limit, **kwargs)
        return ResultSet[StrictTag](output.source, [StrictTag(item) for item in output])

    def select_one(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - These types are copied directly from the parent class
        **kwargs: Any,  # noqa: ANN401 - These types are copied directly from the parent class
    ) -> StrictTag | None:
        """.select_one wrapper that returns a StrctTag object or None.

        Args:
        ----
            selector: The string used to select elements from the source.
            namespaces: The namespaces to use when selecting elements.
            **kwargs: Additional arguments to pass to the parent class's select method.

        Returns:
        -------
            A StrictTag object containing the selected element or None if no match is found.
        """
        output = super().select_one(selector, namespaces, **kwargs)
        if output is not None:
            return StrictTag(output)

        return output

    def strict_select(self, selector: str) -> ResultSet[StrictTag]:
        """.select with simplified parameters that will raise an exception if no matches are found.

        Args:
        ----
            selector: The string used to select elements from the source.

        Returns:
        -------
            A ResultSet containing the selected elements, each wrapped in a StrictTag object.
        """
        output = self.select(selector)
        if len(output) == 0:
            msg = f"No matches found for strict_select({selector})"
            raise StrictSelectError(msg)

        return output

    def strict_select_one(self, selector: str) -> StrictTag:
        """.select_one with simplified parameters that will raise an exception if no matches are found.

        Args:
        ----
            selector: The string used to select elements from the source.

        Returns:
        -------
            A StrictTag object containing the selected element.
        """
        output = self.strict_select(selector)
        if len(output) != 1:
            msg = f"Found {len(output)} matches for strict_select_one({selector})"
            raise StrictSelectError(msg)

        return output[0]

    def strict_get(self, key: str) -> str:
        """.get that will raise an exception if no matches are found.

        Args:
        ----
            key: The string used to select attributes from the element.

        Returns:
        -------
            A string object containing the selected attribute.
        """
        output = self.get(key)
        if not isinstance(output, str):
            msg = f"No matches found for strict_get({key})"
            raise StrictSelectError(msg)

        return output


class StrictTag(StrictMixin):
    """Tag object that has been extended with extra functions."""

    def __init__(self, tag: Tag | None) -> None:
        """Initialize the StrctTag object.

        Args:
        ----
            tag: The Tag object to wrap.
        """
        # Dynamically copy all attributes from the parent class to the child class
        parent_attributes = vars(tag)
        for attr_name, attr_value in parent_attributes.items():
            setattr(self, attr_name, attr_value)


class StrictSoup(BeautifulSoup, StrictMixin):  # type: ignore - This error is present in the original beautifulsoup
    # class because beautifulsoup is a subclass of Tag and beautifulsoup has a reportIncompatibleMethodOverride error in
    # the original code.
    """BeautifulSoup object that has been extended with extra functions."""
