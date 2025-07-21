"""Wait for the application to fulfill a given condition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterable

from screenpy import settings
from screenpy.exceptions import DeliveryError, UnableToAct
from screenpy.pacing import beat
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..abilities import BrowseTheWeb

if TYPE_CHECKING:
    from screenpy import Actor
    from selenium.webdriver.remote.webelement import WebElement
    from typing_extensions import Self

    from ..target import Target


class Wait:
    """Wait for the application to fulfill a given condition.

    Abilities Required:
        :class:`~screenpy_selenium.abilities.BrowseTheWeb`

    Examples::

        the_actor.attempts_to(Wait.for_the(LOGIN_FORM))

        the_actor.attempts_to(
            Wait.for_the(WELCOME_BANNER).to_contain_text("Welcome!")
        )

        the_actor.attempts_to(Wait.for(CONFETTI).to_disappear())

        the_actor.attempts_to(
            Wait(10).seconds_for_the(PARADE_FLOATS).to(float_on_by)
        )

        the_actor.attempts_to(
            Wait().using(cookies_to_contain).with_("delicious=true")
        )

        the_actor.attempts_to(
            Wait().using(
                cookies_to_contain, "for a cookie that has {0}"
            ).with_("delicious=true")
        )

        the_actor.attempts_to(Wait.for_(LOGIN_FORM).polling_every(100).milliseconds()
    """

    args: Iterable[Any]
    timeout: float
    log_detail: str | None

    class _TimeframeBuilder:
        """Build a timeframe, combining numbers and units."""

        def __init__(
            self,
            wait: Wait,
            amount: float,
            attribute: str,
        ) -> None:
            self.wait = wait
            self.amount = amount
            self.attribute = attribute
            setattr(self.wait, self.attribute, self.amount)

        def milliseconds(self) -> Wait:
            """Set the timeout in milliseconds."""
            setattr(self.wait, self.attribute, self.amount / 1000)
            return self.wait

        millisecond = milliseconds

        def seconds(self) -> Wait:
            """Set the timeout in seconds."""
            setattr(self.wait, self.attribute, self.amount)
            return self.wait

        second = seconds

        def perform_as(self, the_actor: Actor) -> None:
            """Just in case the author forgets to use a unit method."""
            the_actor.attempts_to(self.wait)

    def polling(self, amount: float) -> _TimeframeBuilder:
        """Adjust the polling frequency.

        Aliases:
            * ``polling_every``
            * ``trying_every``
        """
        self.poll = amount
        return self._TimeframeBuilder(self, amount, "poll")

    polling_every = trying_every = polling

    @classmethod
    def for_the(cls, target: Target | WebElement) -> Self:
        """Set the Target to wait for.

        Aliases:
            * :meth:`~screenpy_selenium.actions.Wait.for_`
        """
        return cls(seconds=settings.TIMEOUT, args=[target])

    @classmethod
    def for_(cls, target: Target | WebElement) -> Self:
        """Alias for :meth:`~screenpy_selenium.actions.Wait.for_the`."""
        return cls.for_the(target=target)

    def seconds_for_the(self, target: Target | WebElement) -> Self:
        """Set the Target to wait for, after changing the default timeout."""
        self.args = [target]
        return self

    second_for = second_for_the = seconds_for = seconds_for_the

    def using(
        self, strategy: Callable[..., Any], log_detail: str | None = None
    ) -> Self:
        """Use the given strategy to wait for the Target.

        Args:
            strategy: the condition to use to wait. This can be one of
                Selenium's Expected Conditions, or any custom Callable
                that returns a boolean.
            log_detail: a nicer-looking message to log than the default.
                You can use {0}, {1}, etc. to reference specific arguments
                passed into .with_() or .for_the().
        """
        self.condition = strategy
        self.log_detail = log_detail
        return self

    to = seconds_using = using

    def with_(self, *args: Any) -> Self:  # noqa: ANN401
        """Set the arguments to pass in to the wait condition."""
        self.args = args
        return self

    def to_appear(self) -> Self:
        """Use Selenium's "visibility of element located" strategy."""
        return self.using(EC.visibility_of_element_located, "for the {0} to appear...")

    def to_be_clickable(self) -> Self:
        """Use Selenium's "to be clickable" strategy."""
        return self.using(EC.element_to_be_clickable, "for the {0} to be clickable...")

    def to_disappear(self) -> Self:
        """Use Selenium's "invisibility of element located" strategy."""
        return self.using(
            EC.invisibility_of_element_located, "for the {0} to disappear..."
        )

    def to_contain_text(self, text: str) -> Self:
        """Use Selenium's "text to be present in element" strategy."""
        return self.using(
            EC.text_to_be_present_in_element, 'for "{1}" to appear in the {0}...'
        ).with_(*self.args, text)

    @property
    def log_message(self) -> str:
        """Format the nice log message, or give back the default."""
        if self.log_detail is None:
            return f"using {self.condition.__name__} with {self.args}"

        return self.log_detail.format(*self.args)

    def describe(self) -> str:
        """Describe the Action in present tense."""
        return f"Wait {self.timeout} seconds {self.log_message}."

    @beat("{} waits up to {timeout} seconds {log_message}")
    def perform_as(self, the_actor: Actor) -> None:
        """Direct the Actor to wait for the condition to be satisfied."""
        if self.poll > self.timeout:
            msg = "Poll period must be less than or equal to timeout."
            raise UnableToAct(msg)

        browser = the_actor.ability_to(BrowseTheWeb).browser

        try:
            WebDriverWait(browser, self.timeout, self.poll).until(
                self.condition(*self.args)
            )
        except WebDriverException as e:
            msg = (
                f"Encountered an exception using {self.condition.__name__} with "
                f"[{', '.join(map(str, self.args))}]: {e.__class__.__name__}"
            )
            raise DeliveryError(msg) from e

    def __init__(
        self, seconds: float | None = None, args: Iterable[Any] | None = None
    ) -> None:
        self.args = args if args is not None else []
        self.timeout = seconds if seconds is not None else settings.TIMEOUT
        self.condition = EC.visibility_of_element_located
        self.log_detail = None
        self.poll = settings.POLLING
