import pygame
import sys

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 1000, 1000  # Size of the window
ROWS, COLS = 4, 4
SQUARE_SIZE = WIDTH // COLS  # Size of each square

# Colors
WHITE = (238, 221, 130)  # Light Earth Tone
BLACK = (139, 69, 19)    # Dark Earth Tone
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow color for highlighting
CAPTURE_HIGHLIGHT_COLOR = (255, 0, 0)  # Red color for capture directions

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Custom Chess Board with Game Ending Condition')

# Load and scale images
yellow_piece_img = pygame.image.load('images/yellow_piece.png').convert_alpha()
green_piece_img = pygame.image.load('images/green_piece.png').convert_alpha()
scaled_size = 40  # Size of the chess piece image
yellow_piece_img = pygame.transform.scale(yellow_piece_img, (scaled_size, scaled_size))
green_piece_img = pygame.transform.scale(green_piece_img, (scaled_size, scaled_size))

# Define piece positions
yellow_positions = [
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
    (0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5),
    (0, 1), (1, 1), (2, 1), (3, 1), (4, 1)
]
green_positions = [
    (0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
    (0.5, 3.5), (1.5, 3.5), (2.5, 3.5), (3.5, 3.5),
    (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
]

class Piece:
    def __init__(self, x, y, color):
        self.x = x  # Board coordinate x
        self.y = y  # Board coordinate y
        self.color = color  # 'yellow' or 'green'
        self.selected = False

    def draw(self, win):
        blit_x, blit_y = get_blit_pos((self.x, self.y))
        img = green_piece_img if self.color == 'green' else yellow_piece_img
        win.blit(img, (blit_x, blit_y))
        if self.selected:
            pygame.draw.circle(win, HIGHLIGHT_COLOR,
                               (blit_x + scaled_size // 2, blit_y + scaled_size // 2),
                               scaled_size // 2 + 5, 2)

    def move(self, x, y):
        self.x = x
        self.y = y

    def flip(self):
        # Change the piece's color
        self.color = 'green' if self.color == 'yellow' else 'yellow'

def is_vertex(pos):
    return pos[0] % 1 == 0 and pos[1] % 1 == 0

def is_center(pos):
    return pos[0] % 1 == 0.5 and pos[1] % 1 == 0.5

def get_blit_pos(pos):
    x, y = pos
    pixel_x = (x / 4.0) * WIDTH
    pixel_y = (y / 4.0) * HEIGHT
    # Adjust position to center the image
    blit_x = pixel_x - scaled_size // 2
    blit_y = pixel_y - scaled_size // 2
    return blit_x, blit_y

def create_pieces():
    pieces = []
    for pos in yellow_positions:
        piece = Piece(pos[0], pos[1], 'yellow')
        pieces.append(piece)
    for pos in green_positions:
        piece = Piece(pos[0], pos[1], 'green')
        pieces.append(piece)
    return pieces

def draw_board(win, pieces):
    win.fill(WHITE)  # Fill the board with light earth tone
    for row in range(ROWS):
        for col in range(COLS):
            # Draw triangle lines
            top_left = (col * SQUARE_SIZE, row * SQUARE_SIZE)
            top_right = ((col + 1) * SQUARE_SIZE, row * SQUARE_SIZE)
            bottom_left = (col * SQUARE_SIZE, (row + 1) * SQUARE_SIZE)
            bottom_right = ((col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE)
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.line(win, BLACK, top_left, center)
            pygame.draw.line(win, BLACK, top_right, center)
            pygame.draw.line(win, BLACK, bottom_left, center)
            pygame.draw.line(win, BLACK, bottom_right, center)

    # Draw horizontal and vertical lines to create squares
    for i in range(ROWS + 1):
        pygame.draw.line(win, BLACK, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE))
    for i in range(COLS + 1):
        pygame.draw.line(win, BLACK, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT))

    # Draw the pieces
    for piece in pieces:
        piece.draw(win)

def get_piece_at_pos(pieces, pos):
    for piece in pieces:
        if piece.x == pos[0] and piece.y == pos[1]:
            return piece
    return None

def get_valid_moves_for_piece(piece, pieces):
    moves = []

    # Determine the type of the selected piece
    if is_vertex((piece.x, piece.y)):
        # For vertex positions
        directions = [
            # (dx, dy, step_size)
            (0, -1, 1), (1, 0, 1), (0, 1, 1), (-1, 0, 1),  # Orthogonal moves
            (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5)  # Diagonal moves
        ]
    elif is_center((piece.x, piece.y)):
        # For center positions
        directions = [
            (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),
            (0.5, -0.5, 0.5),  (0.5, 0.5, 0.5)
        ]
    else:
        return moves  # Invalid position

    for dx, dy, step_size in directions:
        adj_x = piece.x + dx
        adj_y = piece.y + dy
        land_x = piece.x + 2 * dx
        land_y = piece.y + 2 * dy

        # Check if positions are within bounds
        if 0 <= adj_x <= 4 and 0 <= adj_y <= 4 and 0 <= land_x <= 4 and 0 <= land_y <= 4:
            # Check that the landing position is the same type as the starting position
            if (is_vertex((piece.x, piece.y)) and is_vertex((land_x, land_y))) or \
               (is_center((piece.x, piece.y)) and is_center((land_x, land_y))):
                # Check if adjacent square has a piece and landing square is empty
                if get_piece_at_pos(pieces, (adj_x, adj_y)) and not get_piece_at_pos(pieces, (land_x, land_y)):
                    moves.append((land_x, land_y))
    return moves

def get_valid_moves(selected_piece, pieces):
    return get_valid_moves_for_piece(selected_piece, pieces)

def get_clicked_pos(mouse_pos):
    x = (mouse_pos[0] / WIDTH) * 4.0
    y = (mouse_pos[1] / HEIGHT) * 4.0
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
            if not (0 <= x <= 4 and 0 <= y <= 4):  # Reached the edge of the board
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
        pygame.draw.line(win, CAPTURE_HIGHLIGHT_COLOR, start_pos, end_pos, 5)

def get_pixel_pos(pos):
    x, y = pos
    pixel_x = (x / 4.0) * WIDTH
    pixel_y = (y / 4.0) * HEIGHT
    return (pixel_x, pixel_y)

def has_available_moves(player_color, pieces):
    for piece in pieces:
        if piece.color == player_color:
            valid_moves = get_valid_moves_for_piece(piece, pieces)
            if valid_moves:
                return True
    return False

def main():
    clock = pygame.time.Clock()
    pieces = create_pieces()
    selected_piece = None
    valid_moves = []
    run = True
    game_over = False
    winner = None
    turn = 'green'  # Green pieces go first
    awaiting_capture_choice = False
    capture_options = {}
    moved_piece = None

    while run:
        clock.tick(60)  # Set the frame rate to 60 FPS

        # Check if the current player can move or has any pieces
        if not game_over:
            if not any(p.color == turn for p in pieces) or not has_available_moves(turn, pieces):
                game_over = True
                winner = 'yellow' if turn == 'green' else 'green'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                clicked_pos = get_clicked_pos(mouse_pos)
                piece = get_piece_at_pos(pieces, clicked_pos)

                if awaiting_capture_choice:
                    # Handle capture direction selection
                    dx, dy = None, None
                    # Determine which direction the player clicked
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
                            piece.flip()
                    awaiting_capture_choice = False
                    capture_options = {}
                    moved_piece = None
                    # Switch turn after capturing
                    turn = 'yellow' if turn == 'green' else 'green'
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
                                        piece.flip()
                                # Switch turn after capturing
                                turn = 'yellow' if turn == 'green' else 'green'
                            else:
                                # Multiple capture options, let the player choose
                                awaiting_capture_choice = True
                                moved_piece = selected_piece
                        else:
                            # No captures, switch turn
                            turn = 'yellow' if turn == 'green' else 'green'
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
                            print("No valid moves for this piece.")
                            selected_piece.selected = False
                            selected_piece = None
                    else:
                        print(f"It's {turn}'s turn.")

        draw_board(WIN, pieces)

        # Highlight valid moves
        if selected_piece and valid_moves:
            for move in valid_moves:
                blit_x, blit_y = get_blit_pos(move)
                pygame.draw.circle(WIN, HIGHLIGHT_COLOR,
                                   (blit_x + scaled_size // 2, blit_y + scaled_size // 2),
                                   scaled_size // 2 + 5, 2)

        # If awaiting capture choice, draw capture options
        if awaiting_capture_choice and capture_options:
            draw_capture_options(WIN, moved_piece, capture_options)

        # Display turn information or game over message
        font = pygame.font.SysFont(None, 36)
        if game_over:
            text = f"{winner.capitalize()} Wins!"
            turn_text = font.render(text, True, BLACK)
        else:
            turn_text = font.render(f"{turn.capitalize()}'s Turn", True, BLACK)
        WIN.blit(turn_text, (10, 10))

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
