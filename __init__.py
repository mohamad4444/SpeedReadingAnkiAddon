from aqt.qt import QTimer
from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.sound import play_clicked_audio
from aqt.utils import showInfo

class CustomReviewer(Reviewer):
    """Custom Reviewer class to extend default functionality."""

    def __init__(self, *args, **kwargs):
        # Initialize with the necessary arguments for the base class
        super().__init__(*args, **kwargs)

    def _showQuestion(self):
        """Custom behavior before showing the question."""
        # Call the base class method
        super()._showQuestion()
        QTimer.singleShot(4000, self._showAnswer)
        # Add custom functionality here
        print("Custom behavior: Question is being shown")

    def _showAnswer(self):
        super()._showAnswer()
        QTimer.singleShot(4000, lambda: self._answerCard(1))

    def _answerCard(self, ease):
        """Custom behavior before answering the card."""
        # Call the base class method
        super()._answerCard(ease)
        # Add custom functionality here
        print("Custom behavior: Card is being answered")
    def onButtonClick(self, cmd):
        if cmd == 'custom_action':
            self._handle_custom_action()
        else:
            super().onButtonClick(cmd)

    def _handle_custom_action(self):
        # Implement the functionality for the custom button here
        showInfo("Custom button clicked!")
    def _bottomHTML(self) -> str:
        """Override to add a custom button."""
        base_html = super()._bottomHTML()
        custom_button_html = """
        <td align=end valign=top class=stat>
            <button title="Custom Button" onclick="pycmd('custom_action');">
                Custom Button
            </button>
        </td>
        """
        # Inject the custom button into the existing HTML
        return base_html.replace("</td>\n</tr>", custom_button_html + "</td>\n</tr>")


    def _linkHandler(self, url: str) -> None:
        """Handle custom links."""
        if url == "ans":
            self._getTypedAnswer()
        elif url.startswith("ease"):
            val: Literal[1, 2, 3, 4] = int(url[4:])  # type: ignore
            self._answerCard(val)
        elif url == "edit":
            self.mw.onEditCurrent()
        elif url == "more":
            self.showContextMenu()
        elif url.startswith("play:"):
            play_clicked_audio(url, self.card)
        elif url.startswith("updateToolbar"):
            self.mw.toolbarWeb.update_background_image()
        elif url == "statesMutated":
            self._states_mutated = True
        elif url == "custom_action":
            self._handle_custom_action()
        else:
            print("unrecognized anki link:", url)

    def _handle_custom_action(self):
        """Custom action for the custom button."""
        showInfo("Custom button clicked!")
def replace_reviewer_class():
    """Replace the default Reviewer class with CustomReviewer."""
    if mw.reviewer:
        mw.reviewer.__class__ = CustomReviewer
        print("Custom Reviewer class has been set up.")

def on_reviewer_setup():
    """This function will be called after the reviewer setup."""
    replace_reviewer_class()

def on_anki_ready():
    """Replace the reviewer class once Anki is fully initialized."""
    # Call the custom setup function
    on_reviewer_setup()

from anki.hooks import addHook

addHook('profileLoaded', on_anki_ready)  # Or use another suitable hook
