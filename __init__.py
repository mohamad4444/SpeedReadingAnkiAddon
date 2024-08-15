from anki.hooks import wrap
from aqt import mw
from aqt.qt import QAction, QTimer
from aqt.reviewer import Reviewer
from aqt.utils import showInfo

# Configuration
DELAY_MS_PER_CHARACTER = 1000  # Number of milliseconds per character
FIELDS_TO_CONSIDER = ['Front', 'Back']  # Specify the fields you want to consider

def is_auto_reveal_enabled() -> bool:
    """Check if auto-reveal feature is enabled."""
    return mw.addonManager.getConfig(__name__).get('auto_reveal_enabled', True)

def calculate_delay_from_text(text: str) -> int:
    """Calculate the delay based on the length of the text."""
    num_characters = len(text)
    delay_ms = num_characters * DELAY_MS_PER_CHARACTER
    return delay_ms  # Delay in milliseconds

def get_text_from_fields(card, field_name: str) -> str:
    """Get text from specified field of the card."""
    note = card.note()
    model = note.model()
    fields = note.fields

    # Find the index of the field in the model
    field_index = next((i for i, f in enumerate(model['flds']) if f['name'] == field_name), None)

    if field_index is not None:
        text = fields[field_index]
    else:
        text = ''  # Field not found

    return text

def reveal_after_delay(reviewer: Reviewer):
    """Reveal the answer after a delay."""
    def reveal():
        if reviewer.card and reviewer.state == 'question':
            reviewer._showAnswer()  # Show the answer after the delay

    if reviewer.card:
        question_text = get_text_from_fields(reviewer.card, 'Word')
        delay_ms = calculate_delay_from_text(question_text)
        QTimer.singleShot(delay_ms, reveal)

def on_show_question(reviewer: Reviewer):
    """Callback for showing the question to handle auto-reveal."""
    if is_auto_reveal_enabled():
        reveal_after_delay(reviewer)

# Wrap the Reviewer.show method
Reviewer.show = wrap(Reviewer.show, on_show_question, 'after')

def toggle_auto_reveal():
    """Toggle the auto-reveal feature on or off."""
    config = mw.addonManager.getConfig(__name__)
    current_state = config.get('auto_reveal_enabled', True)
    config['auto_reveal_enabled'] = not current_state
    mw.addonManager.writeConfig(__name__, config)
    status = "enabled" if not current_state else "disabled"
    showInfo(f"Auto-reveal feature has been {status}.")

def setup_menu():
    """Add menu item to toggle the auto-reveal feature."""
    action = QAction("Toggle Auto-Reveal", mw)
    action.triggered.connect(toggle_auto_reveal)
    mw.form.menuTools.addAction(action)

setup_menu()
