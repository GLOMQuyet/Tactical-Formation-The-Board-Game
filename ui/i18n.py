"""Interface text in English and Vietnamese, and the player's language choice.

The choice is kept with the other settings (ui.settings). On the first run
the language follows the computer's locale (Vietnamese or else English).
No pygame here, so the tests can check both languages.
"""

import locale
import os

from ui import settings

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
        'hint_wait': '{color} is thinking: wait for your turn',
        'menu': 'Menu',
        'wins': '{color} wins!',
        'you_win': 'You win!',
        'new_game': 'New game',
        'main_menu': 'Main menu',
        'you_are_out': 'You are out',
        'bots_play_on': 'The bots play on until one is left',
        'watch': 'Watch the bots',
        'settings': 'Settings',
        'sound_on': 'Sound: on',
        'sound_off': 'Sound: off',
        'symbols_on': 'Symbols on pieces: on',
        'symbols_off': 'Symbols on pieces: off',
        'symbols_note': 'Symbols tell the sides apart without colour',
        'folk_on': 'Who goes first: oẳn tù tì',
        'folk_off': 'Who goes first: fixed order',
        'who_first': 'Who goes first?',
        'rule_rps': 'Rock beats scissors, scissors beat paper, paper beats rock',
        'rule_updown': 'Palm down or palm up: whoever differs from the rest drops out',
        'pick_secret': '{color}, choose your hand (others look away!)',
        'pick_yours': 'Choose your hand',
        'hand_rock': 'Rock',
        'hand_scissors': 'Scissors',
        'hand_paper': 'Paper',
        'hand_down': 'Palm down',
        'hand_up': 'Palm up',
        'chant_rps_1': 'Rock...',
        'chant_rps_2': 'paper...',
        'chant_rps_3': 'scissors!',
        'chant_updown_1': 'Palms...',
        'chant_updown_2': 'down or up...',
        'chant_updown_3': 'show!',
        'same_again': 'Same hands: play again!',
        'even_again': 'Nobody stands out: show again!',
        'drops_out': '{color} shows differently and drops out',
        'beats': '{a} beats {b}',
        'goes_first': '{color} goes first!',
        'you_go_first': 'You go first!',
        'start_game': 'Start',
        'skip': 'Skip',
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
        'hint_wait': '{color} đang nghĩ, chờ tới lượt bạn nhé',
        'menu': 'Menu',
        'wins': '{color} thắng!',
        'you_win': 'Bạn thắng!',
        'new_game': 'Ván mới',
        'main_menu': 'Về menu chính',
        'you_are_out': 'Bạn đã bị loại',
        'bots_play_on': 'Các máy chơi tiếp đến khi còn một bên',
        'watch': 'Xem các máy chơi',
        'settings': 'Cài đặt',
        'sound_on': 'Âm thanh: bật',
        'sound_off': 'Âm thanh: tắt',
        'symbols_on': 'Ký hiệu trên quân: bật',
        'symbols_off': 'Ký hiệu trên quân: tắt',
        'symbols_note': 'Ký hiệu giúp phân biệt các phe mà không cần nhìn màu',
        'folk_on': 'Chọn người đi trước: oẳn tù tì',
        'folk_off': 'Chọn người đi trước: thứ tự cố định',
        'who_first': 'Ai đi trước?',
        'rule_rps': 'Búa thắng kéo, kéo thắng bao, bao thắng búa',
        'rule_updown': 'Úp lá xòe: ai ra khác mọi người thì ra ngoài',
        'pick_secret': '{color} chọn tay (người khác đừng nhìn!)',
        'pick_yours': 'Chọn tay của bạn',
        'hand_rock': 'Búa',
        'hand_scissors': 'Kéo',
        'hand_paper': 'Bao',
        'hand_down': 'Úp',
        'hand_up': 'Xòe',
        'chant_rps_1': 'Oẳn tù tì...',
        'chant_rps_2': 'ra cái gì...',
        'chant_rps_3': 'ra cái này!',
        'chant_updown_1': 'Úp...',
        'chant_updown_2': 'lá...',
        'chant_updown_3': 'xòe!',
        'same_again': 'Ra giống nhau: chơi lại!',
        'even_again': 'Không ai khác mọi người: úp xòe lại!',
        'drops_out': '{color} ra khác mọi người nên ra ngoài',
        'beats': '{a} thắng {b}',
        'goes_first': '{color} đi trước!',
        'you_go_first': 'Bạn đi trước!',
        'start_game': 'Vào ván',
        'skip': 'Bỏ qua',
    },
}

COLOR_NAMES = {
    'en': {'green': 'Green', 'yellow': 'Yellow', 'purple': 'Purple', 'blue': 'Blue'},
    'vi': {'green': 'Xanh lá', 'yellow': 'Vàng', 'purple': 'Tím', 'blue': 'Xanh dương'},
}

_lang = None


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
        saved = settings.get('language')
        _lang = saved if saved in LANGS else _from_system()
    return _lang


def set_lang(code, save=True):
    """Switch the interface language and remember it for the next run."""
    global _lang
    _lang = code
    if save:
        settings.put('language', code)


def toggle():
    set_lang('vi' if lang() == 'en' else 'en')


def t(key, **values):
    """Text for `key` in the current language, with `values` filled in."""
    return STRINGS[lang()][key].format(**values)


def color(name):
    """A side's colour name in the current language."""
    return COLOR_NAMES[lang()][name]
