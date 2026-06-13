import pygame
import os
import sys
import asyncio

def resource_path(relative_path):
    """
    Trả về đường dẫn tuyệt đối tới một tệp tài nguyên, hoạt động cho cả PyInstaller và pygbag.

    Parameters:
        relative_path (str): Đường dẫn tương đối tới tệp tài nguyên.

    Returns:
        str: Đường dẫn tuyệt đối tới tệp tài nguyên.
    """
    try:
        # Kiểm tra nếu ứng dụng đang chạy từ PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        try:
            # Lấy đường dẫn tới thư mục chứa script chính (main.py)
            base_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        except AttributeError:
            # Fallback tới thư mục hiện tại nếu không thể xác định được
            base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

WHITE = (255, 255, 255)
WIDTH, HEIGHT = 800, 800
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold
BLACK = (0, 0, 0)

# Deferred — initialised after pygame.init() is called by the entry point
FONT = None
WIN  = None

def _ensure_utils_init():
    global FONT, WIN
    if FONT is None:
        pygame.font.init()
        font_path = resource_path('assets/fonts/Roboto-Bold.ttf')
        FONT = pygame.font.Font(font_path, 36)
    if WIN is None:
        WIN = pygame.display.get_surface()

class Button:
    def __init__(self, text, pos, size, callback):
        self.text = text
        self.pos = pos
        self.size = size
        self.callback = callback
        self.rect = pygame.Rect(pos, size)
        self.hovered = False
        self.font = pygame.font.Font(None, 36)
        self.color = (70, 130, 180) if self.hovered else (65, 105, 225)  # Steel Blue or Royal Blue


    def draw(self, win):
        _ensure_utils_init()
        color = (70, 130, 180) if self.hovered else (65, 105, 225)  # Steel Blue or Royal Blue
        pygame.draw.rect(win, color, self.rect)
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.rect.collidepoint(event.pos):
                return self.callback
        return None
  
    
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

async def game_over_screen(winner, player=None):
    _ensure_utils_init()
    running = True

    restart_button = Button('Restart Game', (WIDTH // 2 - 120, HEIGHT // 2 + 20), (240, 50), player)
    exit_button = Button('Exit', (WIDTH // 2 - 120, HEIGHT // 2 + 90), (240, 50), sys.exit)

    over_text = FONT.render(f'{winner.capitalize()} Wins!', True, HIGHLIGHT_COLOR)
    over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    while running:
        WIN.fill(BLACK)
        WIN.blit(over_text, over_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.rect.collidepoint(event.pos):
                    return "restart"  # Trả về "restart" nếu nhấn nút Restart
                elif exit_button.rect.collidepoint(event.pos):
                    return "exit"  # Trả về "exit" nếu nhấn nút Exit
            restart_button.handle_event(event)
            exit_button.handle_event(event)

        restart_button.draw(WIN)
        exit_button.draw(WIN)

        pygame.display.update()
        await asyncio.sleep(0)

