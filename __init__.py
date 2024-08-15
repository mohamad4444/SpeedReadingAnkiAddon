from aqt.qt import QTimer
from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
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
        # super()._showAnswer()
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


def replace_reviewer_class():
    """Replace the default Reviewer class with CustomReviewer."""
    if mw.reviewer:
        mw.reviewer.__class__ = CustomReviewer
        print("Custom Reviewer class has been set up.")


def on_reviewer_setup():
    """This function will be called after the reviewer setup."""
    replace_reviewer_class()


# Hook into a more generic event if specific reviewer hooks are not available
def on_anki_ready():
    """Replace the reviewer class once Anki is fully initialized."""
    # Call the custom setup function
    on_reviewer_setup()


# Use an existing hook or schedule function if no direct reviewer hooks are found
from anki.hooks import addHook

addHook('profileLoaded', on_anki_ready)  # Or use another suitable hook
