import pygame
import sys
import os
from utils.Button import Button
from utils.utils import is_vertex, is_center, get_piece_at_pos
# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600  # Size of the window
ROWS, COLS = 5, 6  # Updated to 5 rows and 6 columns
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Play game chess with 3 human")

# Colors
WHITE = (255, 255, 255)
SQUARE_SIZE = WIDTH // COLS  # Size of each square

YELLOW_PIECE_IMG = pygame.image.load('assets/yellow_piece.png').convert_alpha()
GREEN_PIECE_IMG = pygame.image.load('assets/green_piece.png').convert_alpha()
PURPLE_PIECE_IMG = pygame.image.load('assets/purple_piece.png').convert_alpha()
YELLOW_PIECE_IMG = pygame.transform.scale(YELLOW_PIECE_IMG, (40, 40))
GREEN_PIECE_IMG = pygame.transform.scale(GREEN_PIECE_IMG, (40, 40))
PURPLE_PIECE_IMG = pygame.transform.scale(PURPLE_PIECE_IMG, (40, 40))
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold

VALID_MOVE_COLOR = (50, 205, 50)  # Lime Green

# Load fonts
FONT = pygame.font.Font('assets/fonts/Roboto-Bold.ttf', 36)
SMALL_FONT = pygame.font.Font('assets/fonts/Roboto-Regular.ttf', 24)

# Load sounds
MOVE_SOUND = pygame.mixer.Sound('assets/sounds/move.mp3')
CAPTURE_SOUND = pygame.mixer.Sound('assets/sounds/capture.mp3')

# Define piece positions
yellow_positions = [
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    (0.5, 0.5), (0.5, 1.5), (0.5, 2.5), (0.5, 3.5),
    (1, 0), (1, 1), (1, 2), (1, 3)
]
green_positions = [
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
    (5.5, 0.5), (5.5, 1.5), (5.5, 2.5), (5.5, 3.5),
    (5, 0), (5, 1), (5, 2), (5, 3)
]
purple_positions = [
    (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
    (1.5, 4.5), (2.5, 4.5), (3.5, 4.5), (4.5, 4.5),
    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4)
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
        else:
            self.image = PURPLE_PIECE_IMG
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
        MOVE_SOUND.play()

    def flip(self):
        self.color = 'green' if self.color == 'yellow' else 'yellow'
        self.image = GREEN_PIECE_IMG if self.color == 'green' else YELLOW_PIECE_IMG
        CAPTURE_SOUND.play()

    def animate(self, win):
        if self.animation_progress > 0:
            current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * (1 - self.animation_progress)
            current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * (1 - self.animation_progress)
            win.blit(self.image, (current_x, current_y))
            self.animation_progress -= 0.05  # Adjust this value to change animation speed
            if self.animation_progress <= 0:
                self.animation_progress = 0
                self.start_pos = None
                self.end_pos = None


def get_blit_pos(pos):
    x, y = pos
    pixel_x = (x / 6.0) * WIDTH - 20
    pixel_y = (y / 6.0) * HEIGHT - 20
    return pixel_x, pixel_y

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
    return pieces

def draw_board(win, pieces):
    BG_IMAGE = pygame.image.load('assets/background.jpg')  # Background image
    win.blit(BG_IMAGE, (0, 0))  # Draw the background image

    # Draw the board lines
    for row in range(ROWS):
        for col in range(COLS):
            if row == ROWS - 1 and (col == 0 or col == COLS - 1):
                continue  # Skip the bottom-left and bottom-right corners
            top_left = (col * SQUARE_SIZE, row * SQUARE_SIZE)
            top_right = ((col + 1) * SQUARE_SIZE, row * SQUARE_SIZE)
            bottom_left = (col * SQUARE_SIZE, (row + 1) * SQUARE_SIZE)
            bottom_right = ((col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE)
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.line(win, WHITE, top_left, center, 5)
            pygame.draw.line(win, WHITE, top_right, center, 5)
            pygame.draw.line(win, WHITE, bottom_left, center, 5)
            pygame.draw.line(win, WHITE, bottom_right, center, 5)

    for i in range(ROWS + 1):
        if i == ROWS:
            pygame.draw.line(win, WHITE, (SQUARE_SIZE, HEIGHT - SQUARE_SIZE), (HEIGHT - SQUARE_SIZE, HEIGHT - SQUARE_SIZE), 5)  # Draw the last horizontal line
        else:
            pygame.draw.line(win, WHITE, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), 5)

    for i in range(COLS + 1):
        if i == 0:
            pygame.draw.line(win, WHITE, (0, 0), (0, HEIGHT - (2*SQUARE_SIZE) ), 5)  # Draw the first vertical line
        elif i == COLS:
            pygame.draw.line(win, WHITE, (WIDTH, 0), (WIDTH, HEIGHT - (2*SQUARE_SIZE)), 5)  # Draw the last vertical line
        else:
            pygame.draw.line(win, WHITE, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT-(WIDTH // COLS)), 5)

    for piece in pieces:
        piece.draw(win)

def get_valid_moves(selected_piece, pieces):
    moves = []

    # Determine the type of the selected piece
    if is_vertex((selected_piece.x, selected_piece.y)):
        # For vertex positions
        directions = [
            # (dx, dy, step_size)
            (0, -1, 1), (1, 0, 1), (0, 1, 1), (-1, 0, 1),  # Orthogonal moves
            (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5)  # Diagonal moves
        ]
    elif is_center((selected_piece.x, selected_piece.y)):
        # For center positions
        directions = [
            (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
            (0.5, -0.5, 0.5),  (0.5, 0.5, 0.5)
        ]
    else:
        return moves  # Invalid position

    for dx, dy, step_size in directions:
        adj_x = selected_piece.x + dx
        adj_y = selected_piece.y + dy
        land_x = selected_piece.x + 2 * dx
        land_y = selected_piece.y + 2 * dy

        # Check if positions are within bounds
        if 0 <= adj_x <= 6 and 0 <= adj_y <= 5 and 0 <= land_x <= 6 and 0 <= land_y <= 5:
            # Check that the landing position is the same type as the starting position
            if (is_vertex((selected_piece.x, selected_piece.y)) and is_vertex((land_x, land_y))) or \
               (is_center((selected_piece.x, selected_piece.y)) and  is_center((land_x, land_y))):
                # Check if adjacent square has a piece and landing square is empty
                if get_piece_at_pos(pieces, (adj_x, adj_y)) and not get_piece_at_pos(pieces, (land_x, land_y)):
                    moves.append((land_x, land_y))
    return moves

def get_clicked_pos(mouse_pos):
    x = (mouse_pos[0] / WIDTH) * 6.0
    y = (mouse_pos[1] / HEIGHT) * 6.0
    # Round to nearest 0.5 to accommodate both vertex and center positions
    clicked_x = round(x * 2) / 2
    clicked_y = round(y * 2) / 2
    return (clicked_x, clicked_y)

def has_available_moves(player_color, pieces):
    for piece in pieces:
        if piece.color == player_color:
            valid_moves = get_valid_moves(piece, pieces)
            if valid_moves:
                return True
    return False

def play_3():
    """Displays a blank Pygame screen."""
        # Start background music
    # pygame.mixer.music.play(-1)

    # clock = pygame.time.Clock()
    pieces = create_pieces()
    selected_piece = None
    valid_moves = []
    run = True
    game_over = False
    winner = None
    # turn = 'green'  # Green pieces go first
    awaiting_capture_choice = False
    capture_options = {}
    moved_piece = None

    while run:
        # clock.tick(120)  # Set the frame rate to 60 FPS
        WIN.fill(WHITE)  # Fill the screen with white 
        
        # Check if the current player can move or has any pieces
        # if not game_over:
        #     if not any(p.color == turn for p in pieces) or not has_available_moves(turn, pieces):
        #         game_over = True
        #         if turn == 'green' and turn == 'yellow':
        #             winner = 'purple'
        #         elif turn == 'green' and turn == 'purple':
        #             winner = 'yellow'
        #         elif turn == 'purple' and turn == 'yellow':
        #             winner = 'green'
        #         else:
        #             winner = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_pos = get_clicked_pos(mouse_pos)
                piece = get_piece_at_pos(pieces, clicked_pos)
                # Only allow selection if the piece belongs to the current player
                if selected_piece:
                    # Try to move to clicked position
                    if clicked_pos in valid_moves:
                        # Move the piece
                        selected_piece.move(clicked_pos[0], clicked_pos[1])
                        selected_piece.selected = False
                        # # Check for captures
                        # capture_options = find_capture_options(pieces, selected_piece)
                        if capture_options:
                            if len(capture_options) == 1:
                                # Only one capture option, perform it automatically
                                for pieces_to_flip in capture_options.values():
                                    for piece in pieces_to_flip:
                                        piece.flip()
                                # Switch turn after capturing
                                # turn = 'yellow' if turn == 'green' else 'green'
                            else:
                                # Multiple capture options, let the player choose
                                awaiting_capture_choice = True
                                moved_piece = selected_piece
                        else:
                            # No captures, switch turn
                            # turn = 'yellow' if turn == 'green' else 'green'
                            pass
                        selected_piece = None
                        valid_moves = []
                    else:
                        selected_piece.selected = False
                        selected_piece = None
                        valid_moves = []
                elif piece and not awaiting_capture_choice:
                    if piece.color:
                        selected_piece = piece
                        selected_piece.selected = True
                        valid_moves = get_valid_moves(selected_piece, pieces)
                        if not valid_moves:
                            selected_piece.selected = False
                            selected_piece = None
        draw_board(WIN,pieces)
        # Highlight valid moves
        if selected_piece and valid_moves:
            for move in valid_moves:
                blit_x, blit_y = get_blit_pos(move)
                pygame.draw.circle(WIN, VALID_MOVE_COLOR,
                                   (blit_x + 20, blit_y + 20),
                                   15, 0)
        pygame.display.update()

if __name__ == "__main__":
    play_3()

