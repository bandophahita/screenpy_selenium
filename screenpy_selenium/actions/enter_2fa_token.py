"""
Enter a 2-factor authentication code into a text field.
"""
from typing import Type, TypeVar

from screenpy.actor import Actor
from screenpy.pacing import beat
from screenpy_pyotp.abilities import AuthenticateWith2FA
from selenium.webdriver.common.action_chains import ActionChains

from ..target import Target
from .enter import Enter

SelfEnter2FAToken = TypeVar("SelfEnter2FAToken", bound="Enter2FAToken")


class Enter2FAToken:
    """Enter the current two-factor authentication token into an input field.

    Abilities Required:
        :class:`~screenpy_selenium.abilities.BrowseTheWeb`
        :external+screenpy_pyotp:class:`~screenpy_pyotp.abilities.AuthenticateWith2FA`

    Examples::

        the_actor.attempts_to(Enter2FAToken.into_the(2FA_INPUT_FIELD))
    """

    @classmethod
    def into_the(cls: Type[SelfEnter2FAToken], target: Target) -> SelfEnter2FAToken:
        """
        Target the element into which to enter the 2FA token.

        Aliases:
            * :meth:`~screenpy_selenium.actions.Enter2FAToken.into`
        """
        return cls(target)

    @classmethod
    def into(cls: Type[SelfEnter2FAToken], target: Target) -> SelfEnter2FAToken:
        """Alias for :meth:`~screenpy_selenium.actions.Enter2FAToken.into_the`."""
        return cls.into_the(target=target)

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Enter a 2FA token into the {self.target}."

    @beat("{} enters their 2FA token into the {target}.")
    def perform_as(self: SelfEnter2FAToken, the_actor: Actor) -> None:
        """Direct the Actor to enter their 2FA token into the element."""
        token = the_actor.uses_ability_to(AuthenticateWith2FA).to_get_token()
        the_actor.attempts_to(Enter.the_text(token).into_the(self.target))

    @beat("  Enter their 2FA token into the {target}!")
    def add_to_chain(
        self: SelfEnter2FAToken, the_actor: Actor, the_chain: ActionChains
    ) -> None:
        """Add the Enter2FAToken Action to a Chain of Actions."""
        token = the_actor.uses_ability_to(AuthenticateWith2FA).to_get_token()
        the_chain.send_keys_to_element(self.target.found_by(the_actor), token)

    def __init__(self: SelfEnter2FAToken, target: Target) -> None:
        self.target = target
