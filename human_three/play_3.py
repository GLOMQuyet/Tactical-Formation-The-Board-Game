import pygame
import sys
import os
from utils.utils import is_vertex, is_center, get_piece_at_pos, resource_path
# Initialize Pygame
pygame.init()

# Define constants
WIDTH_PLAY_3, HEIGHT_PLAY_3 = 800, 800  # Size of the window
ROWS_PLAY_3, COLS_PLAY_3 = 5, 6
SQUARE_SIZE_PLAY_3 = 100  # Size of each square

BOARD_SIZE_PLAY_3 = SQUARE_SIZE_PLAY_3 * COLS_PLAY_3 # 600 x 600 board
# Calculate top-left position to center the board
BOARD_TOP_LEFT_3 = ((WIDTH_PLAY_3 - BOARD_SIZE_PLAY_3) // 2, (HEIGHT_PLAY_3 - BOARD_SIZE_PLAY_3) // 2)  # (100, 100)

bg_path = resource_path('assets/background.jpg')
yellow_path = resource_path('assets/yellow_piece.png')
green_path = resource_path('assets/green_piece.png')
purple_path = resource_path('assets/purple_piece.png')
font_path = resource_path('assets/fonts/Roboto-Bold.ttf')
small_font_path = resource_path('assets/fonts/Roboto-Regular.ttf')
move_sound_path = resource_path('assets/sounds/move.mp3')
capture_sound_path = resource_path('assets/sounds/capture.mp3')
game_over_path = resource_path('assets/sounds/game_over.mp3')
background_path = resource_path('assets/sounds/background_music.mp3')

WIN = pygame.display.set_mode((WIDTH_PLAY_3, HEIGHT_PLAY_3))
pygame.display.set_caption("Play game chess with 3 human")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

YELLOW_PIECE_IMG = pygame.image.load(yellow_path).convert_alpha()
GREEN_PIECE_IMG = pygame.image.load(green_path).convert_alpha()
PURPLE_PIECE_IMG = pygame.image.load(purple_path).convert_alpha()
YELLOW_PIECE_IMG = pygame.transform.scale(YELLOW_PIECE_IMG, (40, 40))
GREEN_PIECE_IMG = pygame.transform.scale(GREEN_PIECE_IMG, (40, 40))
PURPLE_PIECE_IMG = pygame.transform.scale(PURPLE_PIECE_IMG, (40, 40))
BG_IMAGE = pygame.transform.scale(pygame.image.load(bg_path), (1920, 1080))  # Background image

HIGHLIGHT_COLOR = (255, 215, 0)  # Gold
TEXT_COLOR = (0, 255, 255) # Chilli Red
VALID_MOVE_COLOR = (50, 205, 50)  # Lime Green

# Load fonts
FONT = pygame.font.Font(font_path, 36)
SMALL_FONT = pygame.font.Font(small_font_path, 24)

# Load sounds
MOVE_SOUND = pygame.mixer.Sound(move_sound_path)
CAPTURE_SOUND = pygame.mixer.Sound(capture_sound_path)
GAME_OVER_SOUND = pygame.mixer.Sound(game_over_path)
pygame.mixer.music.load(background_path)

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

class Piece:
    def __init__(self, x, y, color):
        self.x = x  # Board coordinate x
        self.y = y  # Board coordinate y
        self.color = color  # 'yellow' or 'green' or 'purple
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
                pygame.draw.circle(win, HIGHLIGHT_COLOR, (int(blit_x + 20), int(blit_y + 20)), 30, 10)
            win.blit(self.image, (blit_x, blit_y))

    def move(self, x, y):
        self.start_pos = get_blit_pos((self.x, self.y))
        self.end_pos = get_blit_pos((x, y))
        self.x = x
        self.y = y
        self.animation_progress = 1  # Start animation
        MOVE_SOUND.play()

    def flip(self, move_color: str):
        if move_color is not None:
            if self.color == "green" or self.color == "yellow":
                self.color =  move_color
            elif self.color == "green" or self.color == "purple": 
                self.color = move_color
            elif self.color:
                self.color = move_color

        if self.color == "green":
            self.image = GREEN_PIECE_IMG
        elif self.color == "purple": 
            self.image = PURPLE_PIECE_IMG
        else:
            self.image = YELLOW_PIECE_IMG
        CAPTURE_SOUND.play()

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
    pixel_x = BOARD_TOP_LEFT_3[0] + x * SQUARE_SIZE_PLAY_3 - 20 # Offset to center the piece image
    pixel_y = BOARD_TOP_LEFT_3[1] + y * SQUARE_SIZE_PLAY_3 - 20
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
    win.blit(BG_IMAGE, (0, 0))  # Draw the background image
    # Draw the board lines
    for row in range(ROWS_PLAY_3):
        for col in range(COLS_PLAY_3):
            if row == ROWS_PLAY_3 - 1 and (col == 0 or col == COLS_PLAY_3 - 1):
                continue  # Skip the bottom-left and bottom-right corners
            top_left = (BOARD_TOP_LEFT_3[0] + col * SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1] + row * SQUARE_SIZE_PLAY_3)
            top_right = (BOARD_TOP_LEFT_3[0] + (col + 1) * SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1] + row * SQUARE_SIZE_PLAY_3)
            bottom_left = (BOARD_TOP_LEFT_3[0] + col * SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1] + (row + 1) * SQUARE_SIZE_PLAY_3)
            bottom_right = (BOARD_TOP_LEFT_3[0] + (col + 1) * SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1] + (row + 1) * SQUARE_SIZE_PLAY_3)
            center = (BOARD_TOP_LEFT_3[0] + col * SQUARE_SIZE_PLAY_3 + SQUARE_SIZE_PLAY_3 // 2, 
                    BOARD_TOP_LEFT_3[1] + row * SQUARE_SIZE_PLAY_3 + SQUARE_SIZE_PLAY_3 // 2)

            pygame.draw.line(win, WHITE, top_left, center, 5)
            pygame.draw.line(win, WHITE, top_right, center, 5)
            pygame.draw.line(win, WHITE, bottom_left, center, 5)
            pygame.draw.line(win, WHITE, bottom_right, center, 5)

    for i in range(ROWS_PLAY_3 + 1):
        if i == ROWS_PLAY_3:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_3[0] + SQUARE_SIZE_PLAY_3,  BOARD_TOP_LEFT_3[1] + BOARD_SIZE_PLAY_3 - SQUARE_SIZE_PLAY_3), (BOARD_TOP_LEFT_3[0] + BOARD_SIZE_PLAY_3 - SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1] + BOARD_SIZE_PLAY_3 - SQUARE_SIZE_PLAY_3), 5)  # Draw the last horizontal line
        else:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_3[0],  BOARD_TOP_LEFT_3[1] + i * SQUARE_SIZE_PLAY_3), (BOARD_TOP_LEFT_3[0] + BOARD_SIZE_PLAY_3,  BOARD_TOP_LEFT_3[1] + i * SQUARE_SIZE_PLAY_3), 5)

    for i in range(COLS_PLAY_3 + 1):
        if i == 0:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_3[0], BOARD_TOP_LEFT_3[1]), (BOARD_TOP_LEFT_3[0], (BOARD_TOP_LEFT_3[1]-(2*SQUARE_SIZE_PLAY_3))  + HEIGHT_PLAY_3 - (2*SQUARE_SIZE_PLAY_3)), 5)  # Draw the first vertical line
        elif i == COLS_PLAY_3:
            pygame.draw.line(win, WHITE, (BOARD_SIZE_PLAY_3 + BOARD_TOP_LEFT_3[0], BOARD_TOP_LEFT_3[1]), (BOARD_SIZE_PLAY_3 + BOARD_TOP_LEFT_3[0], (BOARD_TOP_LEFT_3[1]-(2*SQUARE_SIZE_PLAY_3))  + HEIGHT_PLAY_3 - (2*SQUARE_SIZE_PLAY_3)), 5)  # Draw the last vertical line
        else:
            pygame.draw.line(win, WHITE, (BOARD_TOP_LEFT_3[0] + i * SQUARE_SIZE_PLAY_3, BOARD_TOP_LEFT_3[1]), (BOARD_TOP_LEFT_3[0] + i * SQUARE_SIZE_PLAY_3, BOARD_SIZE_PLAY_3), 5)

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
                    if (land_x, land_y) == (0, 5) or (land_x, land_y) == (0.5, 4.5) or \
                        (land_x, land_y) == (6, 5) or (land_x, land_y) == (5.5, 4.5):
                        continue
                    moves.append((land_x, land_y))
    return moves

def get_clicked_pos(mouse_pos):
    mx, my = mouse_pos

    # Check if the click is within the board area
    if not (BOARD_TOP_LEFT_3[0] - 20 <= mx <= BOARD_TOP_LEFT_3[0] + BOARD_SIZE_PLAY_3 + 20 and
            BOARD_TOP_LEFT_3[1] - 20 <= my <= BOARD_TOP_LEFT_3[1] + BOARD_SIZE_PLAY_3 + 20):
        return None  # Click outside the board

    # Calculate board coordinates without adding SQUARE_SIZE / 2
    x = (mx - BOARD_TOP_LEFT_3[0]) / SQUARE_SIZE_PLAY_3
    y = (my - BOARD_TOP_LEFT_3[1]) / SQUARE_SIZE_PLAY_3

    # Round to nearest 0.5 to accommodate both vertex and center positions
    clicked_x = round(x * 2) / 2
    clicked_y = round(y * 2) / 2

    return (clicked_x, clicked_y)

def find_capture_options(pieces, moved_piece):
    capture_options = {}

    # Determine directions to check
    if is_vertex((moved_piece.x, moved_piece.y)):
        directions = [
            (0, -1), (1, 0), (0, 1), (-1, 0),  # Orthogonal directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
        ]
    elif is_center((moved_piece.x, moved_piece.y)):
        directions = [
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal directions
        ]
    else:
        return {}  # Invalid position

    for dx, dy in directions:
        x, y = moved_piece.x, moved_piece.y
        pieces_to_flip = []
        step_size = 1 if (dx == 0 or dy == 0) else 0.5
        while True:
            x += dx * step_size
            y += dy * step_size
            if not (0 <= x <= 6 and 0 <= y <= 5):  # Reached the edge of the board
                break
            current_piece = get_piece_at_pos(pieces, (x, y))
            
            if current_piece is None:  # Empty space, no capture
                break
            elif current_piece.color != moved_piece.color:  # Enemy piece, add to list to flip
                pieces_to_flip.append(current_piece)
            else:  # Found own piece, capture is possible
                if pieces_to_flip:  # Only add if there are enemy pieces to flip
                    capture_options[(dx, dy)] = list(pieces_to_flip)
                break  # Stop checking this direction
    return capture_options

def draw_capture_options(win, moved_piece, capture_options):
    for direction in capture_options.keys():
        dx, dy = direction
        # Draw an arrow or line in the capture direction
        start_pos = get_pixel_pos((moved_piece.x, moved_piece.y))
        end_x = moved_piece.x + dx
        end_y = moved_piece.y + dy
        end_pos = get_pixel_pos((end_x, end_y))
        pygame.draw.line(win, HIGHLIGHT_COLOR, start_pos, end_pos, 5)

def get_pixel_pos(pos):
    x, y = pos
    pixel_x = BOARD_TOP_LEFT_3[0] + x * SQUARE_SIZE_PLAY_3
    pixel_y = BOARD_TOP_LEFT_3[1] + y * SQUARE_SIZE_PLAY_3
    return (pixel_x, pixel_y)

def has_available_moves(player_color, pieces):
    for piece in pieces:
        if piece.color == player_color:
            valid_moves = get_valid_moves(piece, pieces)
            if valid_moves:
                return True
    return False

def game_over_screen(winner):
    GAME_OVER_SOUND.play()
    running = True

    # Create buttons
    restart_button = Button('Restart Game', (WIDTH_PLAY_3 // 2 - 120, HEIGHT_PLAY_3 // 2 + 20), (240, 50), play_3)
    exit_button = Button('Exit', (WIDTH_PLAY_3 // 2 - 120, HEIGHT_PLAY_3 // 2 + 90), (240, 50), sys.exit)

    while running:
        WIN.fill(BLACK)
        over_text = FONT.render(f'{winner.capitalize()} Wins!', True, HIGHLIGHT_COLOR)
        over_rect = over_text.get_rect(center=(WIDTH_PLAY_3 // 2, HEIGHT_PLAY_3 // 2 - 100))
        WIN.blit(over_text, over_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            restart_button.handle_event(event)
            exit_button.handle_event(event)

        restart_button.draw(WIN)
        exit_button.draw(WIN)

        pygame.display.update()

def play_3():
    """Displays a blank Pygame screen."""
        # Start background music
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    pieces = create_pieces()
    selected_piece = None
    valid_moves = []
    run = True
    game_over = False
    winner = None
    awaiting_capture_choice = False
    capture_options = {}
    moved_piece = None

    # Initialize active players and turn index
    active_players = ['purple', 'yellow', 'green']
    turn_index = 0  # Index to keep track of whose turn it is

    while run:
        clock.tick(120)  # Set the frame rate to 120 FPS
        WIN.fill(WHITE)  # Fill the screen with white 
        
        # Check if the current player can move or has any pieces
        if not game_over:
            # Get the current player's color
            turn = active_players[turn_index % len(active_players)]

            if not any(p.color == turn for p in pieces) or not has_available_moves(turn, pieces):
                active_players.remove(turn)
                turn_index = turn_index + 1
                # Check if only one player is left
                if len(active_players) == 1:
                    game_over = True
                    winner = active_players[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_pos = get_clicked_pos(mouse_pos)
                piece = get_piece_at_pos(pieces, clicked_pos)
                if awaiting_capture_choice:
                    # Handle capture direction selection
                    min_distance = float('inf')
                    selected_direction = None
                    for direction in capture_options.keys():
                        dir_dx, dir_dy = direction
                        end_x = moved_piece.x + dir_dx
                        end_y = moved_piece.y + dir_dy
                        end_pixel = get_pixel_pos((end_x, end_y))
                        distance = ((mouse_pos[0] - end_pixel[0]) ** 2 + (mouse_pos[1] - end_pixel[1]) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            selected_direction = direction
                    if selected_direction:
                        # Perform the capture in the selected direction
                        for piece in capture_options[selected_direction]:
                            piece.flip(move_color=moved_piece.color)
                    awaiting_capture_choice = False
                    capture_options = {}
                    moved_piece = None
                    # Switch turn after capturing
                    turn_index +=1
                
                elif selected_piece:
                    # Try to move to clicked position
                    if clicked_pos in valid_moves:
                        # Move the piece
                        selected_piece.move(clicked_pos[0], clicked_pos[1])
                        selected_piece.selected = False
                        # Check for captures
                        capture_options = find_capture_options(pieces, selected_piece)
                        if capture_options:
                            if len(capture_options) == 1:
                                # Only one capture option, perform it automatically
                                for pieces_to_flip in capture_options.values():
                                    for piece in pieces_to_flip:
                                        piece.flip(move_color=selected_piece.color)
                                # Switch turn after capturing
                                turn_index+=1
                            else:
                                # Multiple capture options, let the player choose
                                awaiting_capture_choice = True
                                moved_piece = selected_piece
                        else:
                            # Switch turn after capturing
                            turn_index+=1
                        selected_piece = None
                        valid_moves = []
                    else:
                        selected_piece.selected = False
                        selected_piece = None
                        valid_moves = []
                elif piece and not awaiting_capture_choice:
                    # Only allow selection if the piece belongs to the current player
                    if piece.color == turn:
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
        # If awaiting capture choice, draw capture options
        if awaiting_capture_choice and capture_options:
            draw_capture_options(WIN, moved_piece, capture_options)
        
        # Display turn information or game over message
        if game_over:
            game_over_screen(winner)
            run = False
        else:
            turn_text = FONT.render(f"{turn.capitalize()}'s Turn", True, TEXT_COLOR)
            WIN.blit(turn_text, (WIDTH_PLAY_3 / 2 - 100, WIDTH_PLAY_3 - 100))
        pygame.display.update()

if __name__ == "__main__":
    play_3()

