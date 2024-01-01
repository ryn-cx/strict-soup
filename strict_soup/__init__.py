"""Extended version of BeautifulSoup with extra functions. WARNING: Modifies BeautifulSoup globally."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from typing_extensions import override


class StrictSelectError(Exception):
    """Exception raised when a strict_* function fails to find a match."""


class StrictMixin(Tag):
    """Mixin for adding extra functions to BeautifulSoup objects."""

    # This is technically a type error because ResultSet[StrctTag] is not a subclass of ResultSet[Tag], there isn't ab
    # obvious fix to this, but this shouldn't cause any problems in practice.
    @override
    def select(
        self,
        selector: str,
        namespaces: Any | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> ResultSet[StrictTag]:
        """.select wrapper that returns a ResultSet[StrictTag].

        Args:
        ----
            selector: A string containing a CSS selector.
            namespaces: A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will use the prefixes it encountered while parsing the document.
            limit: After finding this number of results, stop looking.
            kwargs: Keyword arguments to be passed into SoupSieve's soupsieve.select() method.
        """
        output = super().select(selector, namespaces, limit, **kwargs)
        return ResultSet[StrictTag](output.source, [StrictTag(item) for item in output])

    @override
    def select_one(
        self,
        selector: str,
        namespaces: Any | None = None,
        **kwargs: Any,
    ) -> StrictTag | None:
        """.select_one wrapper that returns a StrctTag or None.

        Args:
        ----
            selector: A string containing a CSS selector.
            namespaces: A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will use the prefixes it encountered while parsing the document.
            kwargs: Keyword arguments to be passed into SoupSieve's soupsieve.select() method.
        """
        output = super().select_one(selector, namespaces, **kwargs)
        if output is not None:
            return StrictTag(output)

        return output

    def strict_select(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - This type is copied directly from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - This type is copied directly from the parent class
    ) -> ResultSet[StrictTag]:
        """.select with simplified parameters that will raise an exception if no matches are found.

        Args:
        ----
            selector: A string containing a CSS selector.
            namespaces: A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will use the prefixes it encountered while parsing the document.
            limit: After finding this number of results, stop looking.
            kwargs: Keyword arguments to be passed into SoupSieve's soupsieve.select() method.

        Raises:
        ------
            StrictSelectError: When no matches are found.
        """
        output = self.select(selector, namespaces, limit, **kwargs)
        if len(output) == 0:
            msg = f"No matches found for strict_select({selector})"
            raise StrictSelectError(msg)

        return output

    def strict_select_one(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - This type is copied directly from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - This type is copied directly from the parent class
    ) -> StrictTag:
        """.select_one with simplified parameters that will raise an exception if no matches are found.

        Args:
        ----
            selector: A string containing a CSS selector.
            namespaces: A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs. By default,
            Beautiful Soup will use the prefixes it encountered while parsing the document.
            limit: After finding this number of results, stop looking.
            kwargs: Keyword arguments to be passed into SoupSieve's soupsieve.select() method.

        Raises:
        ------
            StrictSelectError: When there is not exactly one match.
        """
        output = self.strict_select(selector, namespaces, limit, **kwargs)
        if len(output) != 1:
            msg = f"Found {len(output)} matches for strict_select_one({selector})"
            raise StrictSelectError(msg)

        return output[0]

    def strict_get(self, key: str) -> str:
        """.get that will raise an exception if no matches are found.

        Args:
        ----
            key: The string used to select attributes from the element.

        Raises:
        ------
            StrictSelectError: When no matches are found.
        """
        output = self.get(key)
        if not isinstance(output, str):
            msg = f"No matches found for strict_get({key})"
            raise StrictSelectError(msg)

        return output


class StrictTag(StrictMixin):
    """Tag with extra functions.

    Represents an HTML or XML tag that is part of a parse tree, along with its attributes and contents.

    When Beautiful Soup parses the markup <b>penguin</b>, it will create a Tag object representing the <b> tag.
    """

    def __init__(self, tag: Tag | None) -> None:
        """Initialize the StrctTag object.

        Args:
        ----
            tag: The Tag object to wrap.
        """
        # Dynamically copy all attributes from the parent class to the child class
        self.__dict__.update(vars(tag))


class StrictSoup(BeautifulSoup, StrictMixin):  # type: ignore - This error is present in the original beautifulsoup
    # class because beautifulsoup is a subclass of Tag and beautifulsoup has a reportIncompatibleMethodOverride error in
    # the original code.
    """BeautifulSoup with extra functions.

    A data structure representing a parsed HTML or XML document.

    Most of the methods you'll call on a BeautifulSoup object are inherited from
    PageElement or Tag.

    Internally, this class defines the basic interface called by the
    tree builders when converting an HTML/XML document into a data
    structure. The interface abstracts away the differences between
    parsers. To write a new tree builder, you'll need to understand
    these methods as a whole.

    These methods will be called by the BeautifulSoup constructor:
      * reset()
      * feed(markup)

    The tree builder may call these methods from its feed() implementation:
      * handle_starttag(name, attrs) # See note about return value
      * handle_endtag(name)
      * handle_data(data) # Appends to the current data node
      * endData(containerClass) # Ends the current data node

    No matter how complicated the underlying parser is, you should be
    able to build a tree using 'start tag' events, 'end tag' events,
    'data' events, and "done with data" events.

    If you encounter an empty-element tag (aka a self-closing tag,
    like HTML's <br> tag), call handle_starttag and then
    handle_endtag.
    """
