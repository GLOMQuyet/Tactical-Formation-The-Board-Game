import pygame
import os
import sys

class Config:
    def __init__(self, players=2):
        # Common settings
        self.WIDTH = 800
        self.HEIGHT = 800
        self.asset_paths = {
            'background': 'assets/background.jpg',
            'welcome_background': 'assets/welcome_background.png',
            'yellow_piece': 'assets/yellow_piece.png',
            'green_piece': 'assets/green_piece.png',
            'purple_piece': 'assets/purple_piece.png',
            'blue_piece': 'assets/blue_piece.png',
            'font': 'assets/fonts/Roboto-Bold.ttf',
            'small_font': 'assets/fonts/Roboto-Regular.ttf',
            'move_sound': 'assets/sounds/move.mp3',
            'capture_sound': 'assets/sounds/capture.mp3',
            'game_over_sound': 'assets/sounds/game_over.mp3',
            'background_music': 'assets/sounds/background_music.mp3',
        }
        self.colors = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'HIGHLIGHT_COLOR': (255, 215, 0),
            'VALID_MOVE_COLOR': (50, 205, 50),
        }
        self.players = players
        self.player_colors = ['yellow', 'green', 'purple', 'blue']
        self.set_mode_specific_settings()

    def set_mode_specific_settings(self):
        if self.players == 2:
            self.ROWS = 4
            self.COLS = 4
            self.SQUARE_SIZE = 150
            self.colors['TEXT_COLOR'] = (255, 255, 255)
            self.piece_positions = {
                'yellow': [
                    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                    (0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5),
                    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1)
                ],
                'green': [
                    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
                    (0.5, 3.5), (1.5, 3.5), (2.5, 3.5), (3.5, 3.5),
                    (0, 3), (1, 3), (2, 3), (3, 3), (4, 3)
                ]
            }
        elif self.players == 3:
            self.ROWS = 5
            self.COLS = 6
            self.SQUARE_SIZE = 100
            self.colors['TEXT_COLOR'] = (0, 255, 255)
            self.piece_positions = {
                'yellow': [
                    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                    (0.5, 0.5), (0.5, 1.5), (0.5, 2.5), (0.5, 3.5),
                    (1, 0), (1, 1), (1, 2), (1, 3)
                ],
                'green': [
                    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
                    (5.5, 0.5), (5.5, 1.5), (5.5, 2.5), (5.5, 3.5),
                    (5, 0), (5, 1), (5, 2), (5, 3)
                ],
                'purple': [
                    (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
                    (1.5, 4.5), (2.5, 4.5), (3.5, 4.5), (4.5, 4.5),
                    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4)
                ]
            }
        elif self.players == 4:
            self.ROWS = 6
            self.COLS = 6
            self.SQUARE_SIZE = 100
            self.colors['TEXT_COLOR'] = (0, 255, 255)
            self.piece_positions = {
                'yellow': [
                    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
                    (0.5, 1.5), (0.5, 2.5), (0.5, 3.5), (0.5, 4.5),
                    (1, 2), (1, 3), (1, 4), (1, 5)
                ],
                'green': [
                    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
                    (5.5, 1.5), (5.5, 2.5), (5.5, 3.5), (5.5, 4.5),
                    (5, 1), (5, 2), (5, 3), (5, 4)
                ],
                'purple': [
                    (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
                    (1.5, 5.5), (2.5, 5.5), (3.5, 5.5), (4.5, 5.5),
                    (2, 5), (3, 5), (4, 5), (5, 5)
                ],
                'blue': [
                    (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
                    (1.5, 0.5), (2.5, 0.5), (3.5, 0.5), (4.5, 0.5),
                    (1, 1), (2, 1), (3, 1), (4, 1)
                ]
            }
        else:
            raise ValueError("Unsupported number of players.")

        # Calculate board settings
        self.BOARD_SIZE = self.SQUARE_SIZE * self.COLS
        self.BOARD_TOP_LEFT = ((self.WIDTH - self.BOARD_SIZE) // 2, (self.HEIGHT - self.BOARD_SIZE) // 2)

    def load_assets(self):
        # Load background image
        self.BG_IMAGE = pygame.transform.scale(pygame.image.load(self.asset_paths['background']), (1920, 1080))
        self.WELCOME_BG_IMAGE = pygame.transform.scale(pygame.image.load(self.asset_paths['welcome_background']), (1920, 1080))

        # Load piece images
        self.piece_images = {}
        for color in self.player_colors[:self.players]:
            image_path = self.asset_paths[f'{color}_piece']
            self.piece_images[color] = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (40, 40))

        # Load fonts
        self.FONT = pygame.font.Font(self.asset_paths['font'], 36)
        self.SMALL_FONT = pygame.font.Font(self.asset_paths['small_font'], 24)

        # Load sounds
        self.MOVE_SOUND = pygame.mixer.Sound(self.asset_paths['move_sound'])
        self.CAPTURE_SOUND = pygame.mixer.Sound(self.asset_paths['capture_sound'])
        self.GAME_OVER_SOUND = pygame.mixer.Sound(self.asset_paths['game_over_sound'])
        pygame.mixer.music.load(self.asset_paths['background_music'])

def resource_path(relative_path):
    """ Returns the path to a resource file, even when running from an .exe file """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Otherwise, use the current directory 
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def is_vertex(pos):
    return pos[0] % 1 == 0 and pos[1] % 1 == 0

def is_center(pos):
    return pos[0] % 1 == 0.5 and pos[1] % 1 == 0.5

# Check xem thử bạn có click vào quân cờ hay không , nếu không trả về None
def get_piece_at_pos(pieces, pos):
    for piece in pieces:
        try:
            if piece.x == pos[0] and piece.y == pos[1]:
                return piece
        except:
            continue
    return None

