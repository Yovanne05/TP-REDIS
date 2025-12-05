from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input
from textual import work

from models.conversation import Conversation
from widgets.message_box import MessageBox, FocusableContainer
from commands.command_handler import CommandHandler


class ChatApp(App):
    """Chat app."""

    TITLE = "chat"
    SUB_TITLE = "Une super application de chat"

    BINDINGS = [
        Binding("q", "quit", "Quit", key_display="Q / CTRL+C"),
        ("ctrl+x", "clear", "Clear"),
    ]

    CSS_PATH = "styles.css"

    def compose(self) -> ComposeResult:
        """Yield components."""
        yield Header()
        with FocusableContainer(id="conversation_box"):
            yield MessageBox(
                "Super application de chat!!",
                "INFO : ",
            )
        with Horizontal(id="input_box"):
            yield Input(placeholder="Écrivez votre message", id="message_input")
            yield Button(label="Envoyer", variant="success", id="send_button")
        yield Footer()

    def __init__(self):
        super().__init__()
        self.username = "User"
        self.conversation = Conversation()
        self.command_handler = CommandHandler(self)

    def update_subtitle(self):
        self.sub_title = f"Serveur: {self.conversation.host}:{self.conversation.port} | Canal: {self.conversation.channel}"

    def on_mount(self) -> None:
        """Start the conversation and focus input widget."""
        self.update_subtitle()
        self.listen()
        self.query_one(Input).focus()

    async def action_clear(self) -> None:
        """Clear the conversation and reset widgets."""
        self.conversation.clear()
        conversation_box = self.query_one("#conversation_box")
        await self.conversation.send(len(conversation_box.children))
        await conversation_box.remove()
        self.mount(FocusableContainer(id="conversation_box"))

    async def on_button_pressed(self) -> None:
        await self.process_conversation()

    async def on_input_submitted(self) -> None:
        await self.process_conversation()

    @work(exclusive=True, thread=True)
    def listen(self):
        subscriber = self.conversation.get_subscriber()
        for m in subscriber.listen():
            if m["type"] == "message":
                self.call_from_thread(
                    self._add_message_from_listener, m["data"].decode("utf-8"))

    def _add_message_from_listener(self, message_text):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(
            MessageBox(
                message_text,
                "user ",
            )
        )
        conversation_box.scroll_end(animate=True)

    def add_message(self, message_text):
        conversation_box = self.query_one("#conversation_box")
        conversation_box.mount(
            MessageBox(
                message_text,
                "",
            )
        )
        conversation_box.scroll_end(animate=True)

    async def process_conversation(self) -> None:
        """Process a single question/answer in conversation."""
        message_input = self.query_one("#message_input", Input)

        if message_input.value == "":
            return

        user_message = message_input.value
        button = self.query_one("#send_button")
        conversation_box = self.query_one("#conversation_box")

        self.toggle_widgets(message_input, button)

        with message_input.prevent(Input.Changed):
            message_input.value = ""

        if user_message.startswith("/"):
            parts = user_message[1:].split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            commands = self.command_handler.get_commands()

            if command in commands:
                await commands[command](args, conversation_box)
        else:
            await self.conversation.send(user_message, self.username)

        conversation_box.scroll_end(animate=True)
        self.toggle_widgets(message_input, button)

    def toggle_widgets(self, *widgets: Widget) -> None:
        """Toggle a list of widgets."""
        for w in widgets:
            w.disabled = not w.disabled


if __name__ == "__main__":
    app = ChatApp()
    app.run()
