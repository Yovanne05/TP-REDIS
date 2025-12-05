from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static


class FocusableContainer(Container, can_focus=True):  # type: ignore[call-arg]
    """Focusable container widget."""
    pass


class MessageBox(Widget, can_focus=True):  # type: ignore[call-arg]
    """Box widget for the message."""

    def __init__(self, text: str, role: str) -> None:
        self.text = text
        self.role = role
        super().__init__()

    def compose(self) -> ComposeResult:
        """Yield message component."""
        yield Static(self.role + self.text)
