"""Interface text in English and Vietnamese, and the player's language choice.

The choice is kept in `settings.json` next to the autosave. On the first run
the language follows the computer's locale (Vietnamese or else English).
No pygame here, so the tests can check both languages.
"""

import json
import locale
import os

from core import savegame

LANGS = ('en', 'vi')

STRINGS = {
    'en': {
        'subtitle': 'Cờ Trận · A Vietnamese folk board game',
        'continue': 'Continue',
        'play_human': 'Play Human',
        'play_bot': 'Play Bot',
        'how_to_play': 'How to Play',
        'exit': 'Exit',
        'other_language': 'Tiếng Việt',
        'saved_game': 'Saved game: {game}{level}, {moves} moves played',
        'game_play_2': '2 players',
        'game_play_3_human': '3 players',
        'game_play_4_human': '4 players',
        'game_bot_2': '1 vs Bot (2P)',
        'game_play_3': '1 vs 2 Bots (3P)',
        'game_play_4': '1 vs 3 Bots (4P)',
        'choose_players': 'Choose number of players',
        'players_2': '2 Players',
        'players_3': '3 Players',
        'players_4': '4 Players',
        'back': '<- Back',
        'vs_bot': 'Play vs Bot',
        'you_are_green': 'You always play as Green',
        'difficulty': 'Difficulty',
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard',
        'difficulty_note': 'Harder bots look further ahead and think longer',
        'unfinished': 'Unfinished game',
        'replace_note': 'A new game replaces the saved one',
        'start_new': 'Start new game',
        'keep_saved': 'Continue saved game',
        'turn': "{color}'s turn",
        'your_turn': 'Your turn',
        'thinking': '{color} is thinking...',
        'hint_select': 'Click one of your glowing pieces',
        'hint_move': 'Click a green dot to jump there',
        'hint_capture': 'Several rows are sandwiched: click the one to flip',
        'hint_stuck': 'That piece has nothing to jump over: pick a glowing one',
        'menu': 'Menu',
        'wins': '{color} wins!',
        'you_win': 'You win!',
        'new_game': 'New game',
        'main_menu': 'Main menu',
        'you_are_out': 'You are out',
        'bots_play_on': 'The bots play on until one is left',
        'watch': 'Watch the bots',
    },
    'vi': {
        'subtitle': 'Cờ Trận · Trò chơi cờ dân gian Việt Nam',
        'continue': 'Chơi tiếp',
        'play_human': 'Chơi với người',
        'play_bot': 'Chơi với máy',
        'how_to_play': 'Cách chơi',
        'exit': 'Thoát',
        'other_language': 'English',
        'saved_game': 'Ván đang lưu: {game}{level}, đã đi {moves} nước',
        'game_play_2': '2 người',
        'game_play_3_human': '3 người',
        'game_play_4_human': '4 người',
        'game_bot_2': '1 đấu Máy (2 người)',
        'game_play_3': '1 đấu 2 Máy (3 người)',
        'game_play_4': '1 đấu 3 Máy (4 người)',
        'choose_players': 'Chọn số người chơi',
        'players_2': '2 người',
        'players_3': '3 người',
        'players_4': '4 người',
        'back': '<- Quay lại',
        'vs_bot': 'Chơi với máy',
        'you_are_green': 'Bạn luôn cầm phe Xanh lá',
        'difficulty': 'Độ khó',
        'easy': 'Dễ',
        'medium': 'Vừa',
        'hard': 'Khó',
        'difficulty_note': 'Máy càng khó càng tính xa và nghĩ lâu hơn',
        'unfinished': 'Ván chưa xong',
        'replace_note': 'Ván mới sẽ thay ván đang lưu',
        'start_new': 'Bắt đầu ván mới',
        'keep_saved': 'Chơi tiếp ván đang lưu',
        'turn': 'Lượt của {color}',
        'your_turn': 'Lượt của bạn',
        'thinking': '{color} đang nghĩ...',
        'hint_select': 'Bấm vào một quân đang sáng của bạn',
        'hint_move': 'Bấm vào chấm xanh để nhảy tới đó',
        'hint_capture': 'Kẹp được nhiều hàng: bấm vào hàng muốn lật',
        'hint_stuck': 'Quân này không có quân nào để nhảy qua: chọn quân đang sáng',
        'menu': 'Menu',
        'wins': '{color} thắng!',
        'you_win': 'Bạn thắng!',
        'new_game': 'Ván mới',
        'main_menu': 'Về menu chính',
        'you_are_out': 'Bạn đã bị loại',
        'bots_play_on': 'Các máy chơi tiếp đến khi còn một bên',
        'watch': 'Xem các máy chơi',
    },
}

COLOR_NAMES = {
    'en': {'green': 'Green', 'yellow': 'Yellow', 'purple': 'Purple', 'blue': 'Blue'},
    'vi': {'green': 'Xanh lá', 'yellow': 'Vàng', 'purple': 'Tím', 'blue': 'Xanh dương'},
}

_lang = None


def _settings_path():
    return os.path.join(os.path.dirname(savegame.default_path()), 'settings.json')


def language_for_locale(name):
    """'vi' for a Vietnamese locale name ('vi_VN', 'Vietnamese_Vietnam'), else 'en'."""
    return 'vi' if (name or '').lower().startswith('vi') else 'en'


def _from_system():
    try:
        name = locale.getlocale()[0]
    except ValueError:
        name = None
    return language_for_locale(name or os.environ.get('LANG'))


def lang():
    """The current interface language, 'en' or 'vi'."""
    global _lang
    if _lang is None:
        try:
            with open(_settings_path(), encoding='utf-8') as f:
                saved = json.load(f).get('language')
        except (OSError, ValueError, AttributeError):
            saved = None
        _lang = saved if saved in LANGS else _from_system()
    return _lang


def set_lang(code, save=True):
    """Switch the interface language and remember it for the next run."""
    global _lang
    _lang = code
    if save:
        try:
            os.makedirs(os.path.dirname(_settings_path()), exist_ok=True)
            with open(_settings_path(), 'w', encoding='utf-8') as f:
                json.dump({'language': code}, f)
        except OSError:
            pass   # the choice still holds for this run


def toggle():
    set_lang('vi' if lang() == 'en' else 'en')


def t(key, **values):
    """Text for `key` in the current language, with `values` filled in."""
    return STRINGS[lang()][key].format(**values)


def color(name):
    """A side's colour name in the current language."""
    return COLOR_NAMES[lang()][name]
