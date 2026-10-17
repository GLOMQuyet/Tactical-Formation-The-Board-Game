"""Interface-text tests — both languages complete and consistent.

Run with: uv run python -m unittest tests.test_i18n
"""

import string
import unittest

from core.modes import ALL_MODES
from ui import i18n


def _fields(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


class TestStrings(unittest.TestCase):
    def test_both_languages_have_the_same_keys(self):
        self.assertEqual(set(i18n.STRINGS['en']), set(i18n.STRINGS['vi']))

    def test_placeholders_match(self):
        for key, text in i18n.STRINGS['en'].items():
            self.assertEqual(_fields(text), _fields(i18n.STRINGS['vi'][key]), key)

    def test_every_side_and_game_has_a_name(self):
        for lang in i18n.LANGS:
            for mode in ALL_MODES.values():
                self.assertIn(f'game_{mode.name}', i18n.STRINGS[lang])
                for side in mode.players:
                    self.assertIn(side, i18n.COLOR_NAMES[lang])

    def test_locale_detection(self):
        self.assertEqual(i18n.language_for_locale('vi_VN'), 'vi')
        self.assertEqual(i18n.language_for_locale('Vietnamese_Vietnam'), 'vi')
        self.assertEqual(i18n.language_for_locale('en_US'), 'en')
        self.assertEqual(i18n.language_for_locale(None), 'en')

    def test_text_follows_the_language(self):
        before = i18n.lang()
        try:
            i18n.set_lang('vi', save=False)
            self.assertEqual(i18n.t('wins', color=i18n.color('green')), 'Xanh lá thắng!')
            i18n.set_lang('en', save=False)
            self.assertEqual(i18n.t('wins', color=i18n.color('green')), 'Green wins!')
        finally:
            i18n.set_lang(before, save=False)


if __name__ == '__main__':
    unittest.main()
