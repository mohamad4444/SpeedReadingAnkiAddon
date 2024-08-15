from aqt.qt import QTimer
from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.sound import play_clicked_audio
from aqt.utils import showInfo
import os

miliseconds_per_character = 56
average_reading_speed_per_minute = 238  # words
average_characters_per_word = 4.7
average_speed_per_character = 1000 / (average_reading_speed_per_minute * average_characters_per_word / 60)
average_speed_per_character = 56
class CustomReviewer(Reviewer):
    """Custom Reviewer class to extend default functionality."""

    def __init__(self, *args, **kwargs):
        # Initialize with the necessary arguments for the base class
        super().__init__(*args, **kwargs)

    def log(self,message):
        addon_dir = os.path.dirname(__file__)
        log_file = os.path.join(addon_dir, 'log.txt')
        with open(log_file, 'a') as f:
            f.write(message + '\n')

    def _showQuestion(self):
        """Custom behavior before showing the question."""
        # Call the base class method
        super()._showQuestion()
        note = self.card.note()
        field_text = note['Word']
        reveal_question_delay=len(field_text)*miliseconds_per_character
        self.log(field_text)
        self.log(reveal_question_delay)
        QTimer.singleShot(reveal_question_delay, self._showAnswer)

        # Add custom functionality here
        print("Custom behavior: Question is being shown")

    def _showAnswer(self):
        super()._showAnswer()
        answers_len=0
        for field in ["ArabicTranslation","EnglishTranslation","Example","PluralForm","Gender"]:
            answers_len=answers_len+len(field)
        anwer_fail_delay=answers_len*miliseconds_per_character
        QTimer.singleShot(anwer_fail_delay, lambda: self._answerCard(1))

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

        base_html = """
            <button title="Custom Button" onclick="pycmd('custom_action');">
                Custom Button
            </button>
        """
        base_html+=super()._bottomHTML()
        # Inject the custom button into the existing HTML
        return base_html


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
