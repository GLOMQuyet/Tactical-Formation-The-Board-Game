import pygame
import sys
import os

# Initialize Pygame
pygame.init()

def resource_path(relative_path):
    """ Returns the path to a resource file, even when running from an .exe file """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Otherwise, use the current directory 
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Define constants
WIDTH_PLAY_4, HEIGHT_PLAY_4 = 1000, 1000  # Size of the window
ROWS_PLAY_4, COLS_PLAY_4 = 6, 6
SQUARE_SIZE_PLAY_4 = 150  # Size of each square
LAND = (SQUARE_SIZE_PLAY_4 * ROWS_PLAY_4) - (WIDTH_PLAY_4 - (SQUARE_SIZE_PLAY_4 * 2))
BOARD_SIZE_PLAY_4 = SQUARE_SIZE_PLAY_4 * COLS_PLAY_4 # 900x900 board
# Calculate top-left position to center the board
BOARD_TOP_LEFT_4 = ((WIDTH_PLAY_4 - BOARD_SIZE_PLAY_4) // 2, (HEIGHT_PLAY_4 - BOARD_SIZE_PLAY_4) // 2)  # (100, 100)

WIN = pygame.display.set_mode((WIDTH_PLAY_4, HEIGHT_PLAY_4))
pygame.display.set_caption("Play game chess with 4 human")

# Colors
WHITE = (255, 255, 255)

bg_path = resource_path('assets/background.jpg')
yellow_path = resource_path('assets/yellow_piece.png')
green_path = resource_path('assets/green_piece.png')
purple_path = resource_path('assets/purple_piece.png')
blue_path = resource_path('assets/blue_piece.png')
font_path = resource_path('assets/fonts/Roboto-Bold.ttf')
small_font_path = resource_path('assets/fonts/Roboto-Regular.ttf')
font_path = resource_path('assets/fonts/Roboto-Bold.ttf')
small_font_path = resource_path('assets/fonts/Roboto-Regular.ttf')


BG_IMAGE = pygame.transform.scale(pygame.image.load(bg_path), (1920, 1080))  # Background image
YELLOW_PIECE_IMG = pygame.image.load(yellow_path).convert_alpha()
GREEN_PIECE_IMG = pygame.image.load(green_path).convert_alpha()
PURPLE_PIECE_IMG = pygame.image.load(purple_path).convert_alpha()
BLUE_PIECE_IMG = pygame.image.load(blue_path).convert_alpha()

YELLOW_PIECE_IMG = pygame.transform.scale(YELLOW_PIECE_IMG, (40, 40))
GREEN_PIECE_IMG = pygame.transform.scale(GREEN_PIECE_IMG, (40, 40))
PURPLE_PIECE_IMG = pygame.transform.scale(PURPLE_PIECE_IMG, (40, 40))
BLUE_PIECE_IMG = pygame.transform.scale(BLUE_PIECE_IMG, (40, 40))


HIGHLIGHT_COLOR = (255, 215, 0)  # Gold

# Load fonts
FONT = pygame.font.Font(font_path, 36)
SMALL_FONT = pygame.font.Font(small_font_path, 24)

# Define piece positions

blue_positions = [
    (1, 0),(2, 0), (3, 0), (4, 0), (5, 0),
    (1.5, 0.5), (2.5, 0.5), (3.5, 0.5), (4.5, 0.5),
    (1, 1), (2, 1), (3, 1), (4, 1),
]

yellow_positions = [
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
    (0.5, 1.5), (0.5, 2.5), (0.5, 3.5), (0.5, 4.5),
    (1, 2), (1, 3), (1, 4), (1, 5)
]
purple_positions = [
    (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
    (1.5, 5.5), (2.5, 5.5), (3.5, 5.5), (4.5, 5.5),
    (2, 5), (3, 5), (4, 5), (5, 5)
]

green_positions = [
    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
    (5.5, 1.5), (5.5, 2.5), (5.5, 3.5), (5.5, 4.5),
    (5, 1), (5, 2), (5, 3), (5, 4)
]



class Piece:
    def __init__(self, x, y, color):
        self.x = x  # Board coordinate x
        self.y = y  # Board coordinate y
        self.color = color  # 'yellow' or 'green'
        self.selected = False
        if color == 'yellow':
            self.image = YELLOW_PIECE_IMG
        elif color == 'green':
            self.image = GREEN_PIECE_IMG
        elif color == 'blue':
            self.image = PURPLE_PIECE_IMG
        else:
            self.image = BLUE_PIECE_IMG

        self.animation_progress = 0  # For animations
        self.start_pos = None
        self.end_pos = None

    def draw(self, win):
        if self.animation_progress > 0:
            self.animate(win)
        else:
            blit_x, blit_y = get_blit_pos((self.x, self.y))
            if self.selected:
                pygame.draw.circle(win, HIGHLIGHT_COLOR, (blit_x + 20, blit_y + 20), 30, 10)
            win.blit(self.image, (blit_x, blit_y))

    def move(self, x, y):
        self.start_pos = get_blit_pos((self.x, self.y))
        self.end_pos = get_blit_pos((x, y))
        self.x = x
        self.y = y
        self.animation_progress = 1  # Start animation

    def flip(self):
        self.color = 'green' if self.color == 'yellow' else 'yellow'
        self.image = GREEN_PIECE_IMG if self.color == 'green' else YELLOW_PIECE_IMG

    def animate(self, win):
        if self.animation_progress > 0:
            current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * (1 - self.animation_progress)
            current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * (1 - self.animation_progress)
            win.blit(self.image, (current_x, current_y))
            self.animation_progress -= 1e-1  # Adjust this value to change animation speed
            if self.animation_progress <= 0:
                self.animation_progress = 0
                self.start_pos = None
                self.end_pos = None

def get_blit_pos(pos):
    x, y = pos
    pixel_x = BOARD_TOP_LEFT_4[0] + x * SQUARE_SIZE_PLAY_4 - 20 # Offset to center the piece image
    pixel_y = BOARD_TOP_LEFT_4[1] + y * SQUARE_SIZE_PLAY_4 - 20
    return pixel_x, pixel_y

def get_clicked_pos(mouse_pos):
    mx, my = mouse_pos

    # Check if the click is within the board area
    if not (BOARD_TOP_LEFT_4[0] - 20 <= mx <= BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4 + 20 and
            BOARD_TOP_LEFT_4[1] - 20 <= my <= BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4 + 20):
        return None  # Click outside the board

    # Calculate board coordinates without adding SQUARE_SIZE / 2
    x = (mx - BOARD_TOP_LEFT_4[0]) / SQUARE_SIZE_PLAY_4
    y = (my - BOARD_TOP_LEFT_4[1]) / SQUARE_SIZE_PLAY_4

    # Round to nearest 0.5 to accommodate both vertex and center positions
    clicked_x = round(x * 2) / 2
    clicked_y = round(y * 2) / 2

    return (clicked_x, clicked_y)

def draw_board(win, pieces):
    win.blit(BG_IMAGE, (0, 0))  # Draw the background image

    # Draw the board lines
    for row in range(ROWS_PLAY_4):
        for col in range(COLS_PLAY_4):
            if row == ROWS_PLAY_4 - 1 and (col == 0 or col == COLS_PLAY_4 - 1):
                continue  # Skip the bottom-left and bottom-right corners
            elif row == 0 and (col == 0 or col == COLS_PLAY_4 - 1):
                continue
            top_left = (BOARD_TOP_LEFT_4[0] + col * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + row * SQUARE_SIZE_PLAY_4)
            top_right = (BOARD_TOP_LEFT_4[0] +(col + 1) * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + row * SQUARE_SIZE_PLAY_4)
            bottom_left = (BOARD_TOP_LEFT_4[0] +col * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + (row + 1) * SQUARE_SIZE_PLAY_4)
            bottom_right = (BOARD_TOP_LEFT_4[0] +(col + 1) * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + (row + 1) * SQUARE_SIZE_PLAY_4)
            center = (BOARD_TOP_LEFT_4[0] + col * SQUARE_SIZE_PLAY_4 + SQUARE_SIZE_PLAY_4 // 2, BOARD_TOP_LEFT_4[1] + row * SQUARE_SIZE_PLAY_4 + SQUARE_SIZE_PLAY_4 // 2)
            pygame.draw.line(win, WHITE, top_left, center, 5)
            pygame.draw.line(win, WHITE, top_right, center, 5)
            pygame.draw.line(win, WHITE, bottom_left, center, 5)
            pygame.draw.line(win, WHITE, bottom_right, center, 5)

    for i in range(ROWS_PLAY_4 + 1):
        if i == 0:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0] + SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1]), (BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4 - SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1]), 5)  # Draw the last horizontal line
        elif i == ROWS_PLAY_4:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0] + SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4), (BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4 - SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4), 5) 
        else:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0] , BOARD_TOP_LEFT_4[1] + i * SQUARE_SIZE_PLAY_4), (BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + i * SQUARE_SIZE_PLAY_4), 5)

    for i in range(COLS_PLAY_4 + 1):
        if i == 0:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0], BOARD_TOP_LEFT_4[1] + SQUARE_SIZE_PLAY_4), (BOARD_TOP_LEFT_4[0], BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4 - SQUARE_SIZE_PLAY_4), 5)  # Draw the first vertical line
        elif i == COLS_PLAY_4:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + SQUARE_SIZE_PLAY_4), (BOARD_TOP_LEFT_4[0] + BOARD_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4 - SQUARE_SIZE_PLAY_4), 5)  # Draw the last vertical line
        else:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_4[0] + i * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1]), (BOARD_TOP_LEFT_4[0] + i * SQUARE_SIZE_PLAY_4, BOARD_TOP_LEFT_4[1] + BOARD_SIZE_PLAY_4), 5)


    for piece in pieces:
        piece.draw(win)

def create_pieces():
    pieces = []
    for pos in yellow_positions:
        piece = Piece(pos[0], pos[1], 'yellow')
        pieces.append(piece)
    for pos in green_positions:
        piece = Piece(pos[0], pos[1], 'green')
        pieces.append(piece)
    for pos in purple_positions:
        piece = Piece(pos[0], pos[1], 'purple')
        pieces.append(piece)
    for pos in blue_positions:
        piece = Piece(pos[0], pos[1], 'blue')
        pieces.append(piece)
    return pieces

def play_4():
    """Displays a blank Pygame screen."""
    running = True
    pieces = create_pieces()
    while running:
        WIN.fill(WHITE)  # Fill the screen with white 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_pos = get_clicked_pos(mouse_pos)
                print("Tick",clicked_pos)
        draw_board(WIN,pieces)
        pygame.display.update()

if __name__ == "__main__":
    play_4()

