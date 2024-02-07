"""Matches a clickable WebElement."""

from __future__ import annotations

from typing import TYPE_CHECKING

from screenpy.resolutions.base_resolution import BaseResolution

from .custom_matchers import is_clickable_element

if TYPE_CHECKING:
    from .custom_matchers.is_clickable_element import IsClickableElement


class IsClickable(BaseResolution):
    """Match on a clickable element.

    Examples::

        the_actor.should(See.the(Element(LOGIN_BUTTON), IsClickable()))
    """

    matcher: IsClickableElement
    line = "clickable"
    matcher_function = is_clickable_element

    def __init__(self) -> None:  # pylint: disable=useless-super-delegation
        super().__init__()
