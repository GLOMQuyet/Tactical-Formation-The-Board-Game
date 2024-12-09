import pygame
import os
import sys

pygame.font.init()

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

font_path = resource_path('assets/fonts/Roboto-Bold.ttf')
FONT = pygame.font.Font(font_path, 36)

WHITE = (255, 255, 255)
class Button:
    def __init__(self, text, pos, size, callback):
        self.text = text
        self.pos = pos
        self.size = size
        self.callback = callback
        self.rect = pygame.Rect(pos, size)
        self.hovered = False

    def draw(self, win):
        color = (70, 130, 180) if self.hovered else (65, 105, 225)  # Steel Blue or Royal Blue
        pygame.draw.rect(win, color, self.rect)
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()
            
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

