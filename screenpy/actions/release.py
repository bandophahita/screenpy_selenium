"""
An action to release the left mouse button or a held modifier key. This action
expects that a |HoldDown| action was called earlier in the |Chain|. An actor
must possess the ability to BrowseTheWeb to perform this action. An actor
performs this action like so:

    the_actor.attempts_to(Chain(Release.the_alt_key()))

    the_actor.attempts_to(
        Chain(Release.left_mouse_button().on_the(DRAGGABLE_BOX))
    )
"""


import platform
from typing import Optional

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from ..actor import Actor
from ..exceptions import UnableToAct
from ..pacing import beat
from .base_action import BaseAction
from .hold_down import KEY_NAMES


class Release(BaseAction):
    """
    Releases the specified key or left mouse button. This action can only be
    used with the |Chain| meta-action, and it is expected that a corresponding
    |HoldDown| action was called earlier in the Chain.

    A Release action is expected to be instantiated via one of its static
    methods, or on its own with a specific key. A typical invocation might
    look like:

        Release.left_mouse_button()

        Release(Keys.SHIFT)

        Release.command_or_control_key()

    It can then be passed along to the |Actor| in a Chain to perform the
    action.
    """

    @staticmethod
    def command_or_control_key() -> "Release":
        """
        A convenience method that figures out what operating system the actor
        is using and tells the actor which execution key to release.

        Returns:
            |Release|
        """
        if platform.system() == "Darwin":
            return Release(Keys.COMMAND)
        return Release(Keys.CONTROL)

    @staticmethod
    def left_mouse_button() -> "Release":
        """
        Indicates the Release action should release the left mouse button.

        Returns:
            |Release|
        """
        return Release(lmb=True)

    def perform_as(self, the_actor: Actor) -> None:
        """
        Raises an exception. A Release action cannot be directly performed,
        it must be used with |Chain|.

        Raises:
            |UnableToAct|: always.
        """
        raise UnableToAct(
            "The Release action cannot be performed directly, "
            "it can only be used with the Chain action."
        )

    @beat("  Releases the {description}!")
    def add_to_chain(self, the_actor: Actor, the_chain: ActionChains) -> None:
        """
        Adds the configured Release action to an in-progress |Chain| of
        actions.

        Args:
            the_actor: the |Actor| who will be performing the action chain.
            the_chain: the |ActionChains| instance that is being built.

        Raises:
            |UnableToAct|: if the action was not told what to release.
        """
        if self.lmb:
            the_chain.release()
        elif self.key is not None:
            the_chain.key_up(self.key)
        else:
            raise UnableToAct("Release must be told what to release.")

    def __init__(self, key: Optional[str] = None, lmb: bool = False) -> None:
        self.key = key
        self.lmb = lmb
        self.description = "LEFT MOUSE BUTTON" if lmb else KEY_NAMES[key]
