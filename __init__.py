from aqt.qt import QTimer, QAction, QMenu
from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from aqt.sound import play_clicked_audio
from aqt.utils import showInfo, getText
import os

miliseconds_per_character = 150
average_reading_speed_per_minute = 238  # words
average_characters_per_word = 4.7
average_speed_per_character = 1000 / (average_reading_speed_per_minute * average_characters_per_word / 60)
average_speed_per_character = 56


# Store the state of autofail and auto-show-answer
def get_config():
    return mw.col.get_config('custom_review_settings', {'autofail': True, 'auto_show_answer': True})


def set_config(autofail, auto_show_answer):
    mw.col.set_config('custom_review_settings', {'autofail': autofail, 'auto_show_answer': auto_show_answer})


class CustomReviewer(Reviewer):
    """Custom Reviewer class to extend default functionality."""

    def __init__(self, *args, **kwargs):
        # Initialize with the necessary arguments for the base class
        super().__init__(*args, **kwargs)

    def log(self, message):
        addon_dir = os.path.dirname(__file__)
        log_file = os.path.join(addon_dir, 'log.txt')
        with open(log_file, 'a') as f:
            f.write(str(message) + '\n')

    def _showQuestion(self):
        """Custom behavior before showing the question."""
        # Call the base class method
        super()._showQuestion()
        note = self.card.note()
        field_text = note['Word']

        config = get_config()

        if config['auto_show_answer']:
            reveal_question_delay = len(field_text) * miliseconds_per_character
            self.log(field_text)
            self.log(reveal_question_delay)
            QTimer.singleShot(reveal_question_delay, self._showAnswer)
        else:
            print("Auto-show answer is disabled")

    def _showAnswer(self):
        super()._showAnswer()

        config = get_config()
        if config['autofail']:
            answers_len = 0
            for field in ["ArabicTranslation", "EnglishTranslation", "Example", "PluralForm", "Gender"]:
                answers_len += len(self.card.note()[field])
            anwer_fail_delay = answers_len * miliseconds_per_character
            QTimer.singleShot(anwer_fail_delay, lambda: self._answerCard(1))
        else:
            print("Autofail is disabled")

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
        """Custom action for the custom button."""
        config = get_config()
        autofail = not config['autofail']

        auto_show_answer = not config['auto_show_answer']
        set_config(autofail, auto_show_answer)
        self.log(config)
        # self.log(f"Autofail {'enabled' if autofail else 'disabled'}, Auto-Show Answer {'enabled' if auto_show_answer else 'disabled'}")
        # showInfo(
        #     f"Autofail {'enabled' if autofail else 'disabled'}, Auto-Show Answer {'enabled' if auto_show_answer else 'disabled'}")

        # Update the button HTML to reflect the current state
        self.update_bottom_html()

    def update_bottom_html(self):
        """Update the HTML of the custom button to reflect current settings."""
        self._bottomHTML()

    def _bottomHTML(self) -> str:
        """Override to add a custom button."""
        config = get_config()
        autofail_status = 'enabled' if config['autofail'] else 'disabled'
        auto_show_answer_status = 'enabled' if config['auto_show_answer'] else 'disabled'

        base_html = f"""
            <button title="Custom Button" onclick="pycmd('custom_action');">
                Custom Button: Autofail {autofail_status}, Auto-Show Answer {auto_show_answer_status}
            </button>
        """
        base_html += super()._bottomHTML()
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


# Add menu options to toggle features
def setup_menu():
    menu = QMenu('Custom Review Settings', mw)
    autofail_action = QAction('Toggle Autofail', mw)
    auto_show_answer_action = QAction('Toggle Auto-Show Answer', mw)

    def toggle_autofail():
        config = get_config()
        new_value = not config['autofail']
        set_config(new_value, config['auto_show_answer'])
        showInfo(f"Autofail {'enabled' if new_value else 'disabled'}")

    def toggle_auto_show_answer():
        config = get_config()
        new_value = not config['auto_show_answer']
        set_config(config['autofail'], new_value)
        showInfo(f"Auto-Show Answer {'enabled' if new_value else 'disabled'}")

    autofail_action.triggered.connect(toggle_autofail)
    auto_show_answer_action.triggered.connect(toggle_auto_show_answer)

    menu.addAction(autofail_action)
    menu.addAction(auto_show_answer_action)

    mw.form.menuTools.addMenu(menu)


addHook('setupMenus', setup_menu)
