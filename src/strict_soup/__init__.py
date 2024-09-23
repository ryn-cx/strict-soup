"""Extended version of BeautifulSoup with extra functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from _typeshed import SupportsRead
    from bs4 import SoupStrainer
    from bs4.builder import TreeBuilder
    from bs4.element import PageElement


def _convert_to_strict_tag(tag: Tag | None) -> StrictTag:
    """Convert a Tag to a StrictTag.

    Args:
        tag: The Tag object to convert or None.

    Returns:
        A StrictTag or None.
    """
    # There may be an error in beautifulsoup's types where None can be passed
    # into this function. This is here to see if that ever occurs and the code
    # can be modified if that does occur.
    if tag is None:
        msg = "Cannot convert None to StrictTag"
        raise ValueError(msg)

    tag.__class__ = StrictTag
    return cast(StrictTag, tag)


class StrictSelectError(Exception):
    """Exception raised when a strict_* function fails to find a match."""


class StrictTag(Tag):
    """Mixin for adding extra functions to BeautifulSoup objects."""

    # This is technically a type error because ResultSet[StrictTag] is not a real
    # subclass of ResultSet[Tag]. There isn't an obvious fix, but it shouldn't
    # cause any noticeable issues.
    @override
    def select(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        selector: str,
        namespaces: Any | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> ResultSet[StrictTag]:
        """.select wrapper that returns a ResultSet[StrictTag].

        Perform a CSS selection operation on the current element.

        This uses the SoupSieve library.

        Args:
            selector: A string containing a CSS selector.

            namespaces: A dictionary mapping namespace prefixes used in the CSS
                selector to namespace URIs. By default, Beautiful Soup will use
                the prefixes it encountered while parsing the document.

            limit: After finding this number of results, stop looking.

            kwargs: Keyword arguments to be passed into SoupSieve's
                soupsieve.select() method.

        Returns:
            A ResultSet of StrictTag objects.
        """
        output = super().select(selector, namespaces, limit, **kwargs)
        return ResultSet(
            output.source,
            [_convert_to_strict_tag(item) for item in output],
        )

    @override
    def select_one(
        self,
        selector: str,
        namespaces: Any | None = None,
        **kwargs: Any,
    ) -> StrictTag | None:
        """.select_one wrapper that returns a StrictTag or None.

        Perform a CSS selection operation on the current element.

        Args:
            selector: A string containing a CSS selector.

            namespaces: A dictionary mapping namespace prefixes used in the CSS
                selector to namespace URIs. By default, Beautiful Soup will use
                the prefixes it encountered while parsing the document.

            kwargs: Keyword arguments to be passed into SoupSieve's
                soupsieve.select() method.

        Returns:
            A StrictTag or None.
        """
        output = super().select_one(selector, namespaces, **kwargs)
        if output is not None:
            return _convert_to_strict_tag(output)

        return output

    def strict_select(
        self,
        selector: str,
        namespaces: Any | None = None,  # noqa: ANN401 - Copied from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - Copied from the parent class
    ) -> ResultSet[StrictTag]:
        """.select that will raise an exception if no matches are found.

        Perform a CSS selection operation on the current element.

        This uses the SoupSieve library.

        Args:
            selector: A string containing a CSS selector.

            namespaces: A dictionary mapping namespace prefixes used in the CSS
                selector to namespace URIs. By default, Beautiful Soup will use
                the prefixes it encountered while parsing the document.

            limit: After finding this number of results, stop looking.

            kwargs: Keyword arguments to be passed into SoupSieve's
                soupsieve.select() method.

        Raises:
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
        namespaces: Any | None = None,  # noqa: ANN401 - Copied from the parent class
        limit: int | None = None,
        **kwargs: Any,  # noqa: ANN401 - Copied from the parent class
    ) -> StrictTag:
        """.select_one that will raise an exception if no matches are found.

        Perform a CSS selection operation on the current element.

        Args:
            selector: A string containing a CSS selector.

            namespaces: A dictionary mapping namespace prefixes used in the CSS
                selector to namespace URI2s. By default, Beautiful Soup will use
                the prefixes it encountered while parsing the document.

            limit: After finding this number of results, stop looking.

            kwargs: Keyword arguments to be passed into SoupSieve's
                soupsieve.select() method.

        Raises:
            StrictSelectError: When there is not exactly one match.
        """
        output = self.strict_select(selector, namespaces, limit, **kwargs)
        if len(output) != 1:
            msg = f"Found {len(output)} matches for strict_select_one({selector})"
            raise StrictSelectError(msg)

        return output[0]

    def strict_get(self, key: str) -> str:
        """.get that will raise an exception if no matches are found.

        Returns the value of the 'key' attribute for the tag, or the value given
        for 'default' if it doesn't have that attribute.

        Args:
            key: The string used to select attributes from the element.

        Raises:
            StrictSelectError: When no matches are found.
        """
        output = self.get(key)
        if not isinstance(output, str):
            msg = f"No matches found for strict_get({key})"
            raise StrictSelectError(msg)

        return output


# This error is present in the original beautifulsoup class because
# beautifulsoup is a subclass of Tag and beautifulsoup has a
# reportIncompatibleMethodOverride error in the original code.
class StrictSoup(BeautifulSoup, StrictTag):  # type: ignore[reportIncompatibleMethodOverride]
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

    def insert_after(self, *args: PageElement | str) -> None:
        """Dummy function that raises an error."""
        msg = f"This is not implemented, the args of {args} do nothing."
        raise NotImplementedError(msg)

    def insert_before(self, *args: PageElement | str) -> None:
        """Dummy function that raises an error."""
        msg = f"This is not implemented, the args of {args} do nothing."
        raise NotImplementedError(msg)

    @override
    def __init__(
        self,
        markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = "",
        features: str | Sequence[str] | None = "lxml",
        builder: TreeBuilder | type[TreeBuilder] | None = None,
        parse_only: SoupStrainer | None = None,
        from_encoding: str | None = None,
        exclude_encodings: Sequence[str] | None = None,
        element_classes: dict[type[PageElement], type[Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        # This error is from bs4 itself and can be ignored.
        super().__init__(  # type: ignore[reportIncompatibleMethodOverride]
            markup,
            features,
            builder,
            parse_only,
            from_encoding,
            exclude_encodings,
            element_classes,
            **kwargs,
        )
