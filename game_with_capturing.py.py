import pygame
import sys

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 800  # Size of the window
ROWS, COLS = 4, 4
SQUARE_SIZE = WIDTH // COLS  # Colors
WHITE = (238, 221, 130)  # Light Earth Tone
BLACK = (139, 69, 19)  # Dark Earth Tone
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow color for highlighting

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Custom Chess Board with Capturing Mechanics')

# Load and scale images
yellow_piece_img = pygame.image.load('images/yellow_piece.png').convert_alpha()
green_piece_img = pygame.image.load('images/green_piece.png').convert_alpha()
scaled_size = 40  # Make the chess piece image smaller
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
                               (blit_x + scaled_size // 2, blit_y + scaled_size // 2), scaled_size // 2 + 5, 2)

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


def get_valid_moves(selected_piece, pieces):
    moves = []
    # Determine the type of the selected piece
    if is_vertex((selected_piece.x, selected_piece.y)):
        step = 1  # For vertex positions
        # Orthogonal directions
        directions = [(-step, 0), (step, 0), (0, -step), (0, step)]
    elif is_center((selected_piece.x, selected_piece.y)):
        step = 0.5  # For center positions
        # Diagonal directions
        directions = [(-step, -step), (-step, step), (step, -step), (step, step)]
    else:
        return moves  # Invalid position

    for dx, dy in directions:
        adj_x = selected_piece.x + dx
        adj_y = selected_piece.y + dy
        land_x = selected_piece.x + 2 * dx
        land_y = selected_piece.y + 2 * dy

        # Check if positions are within bounds
        if 0 <= adj_x <= 4 and 0 <= adj_y <= 4 and 0 <= land_x <= 4 and 0 <= land_y <= 4:
            # Check that the landing position is the same type
            if (is_vertex((selected_piece.x, selected_piece.y)) and is_vertex((land_x, land_y))) or \
                    (is_center((selected_piece.x, selected_piece.y)) and is_center((land_x, land_y))):
                # Check if adjacent square has a piece and landing square is empty
                if get_piece_at_pos(pieces, (adj_x, adj_y)) and not get_piece_at_pos(pieces, (land_x, land_y)):
                    moves.append((land_x, land_y))
                    # Debugging output to show why move is allowed
                    # print(f"Valid move for piece at ({selected_piece.x}, {selected_piece.y}) to ({land_x}, {land_y}) by jumping over ({adj_x}, {adj_y})")
    return moves


def get_clicked_pos(mouse_pos):
    x = (mouse_pos[0] / WIDTH) * 4.0
    y = (mouse_pos[1] / HEIGHT) * 4.0
    # Round to nearest 0.5 to accommodate both vertex and center positions
    clicked_x = round(x * 2) / 2
    clicked_y = round(y * 2) / 2
    return (clicked_x, clicked_y)


def capture_pieces(pieces, moved_piece):
    # Determine directions to check
    if is_vertex((moved_piece.x, moved_piece.y)):
        step = 1  # All 8 directions for vertex positions
        directions = [(-step, 0), (step, 0), (0, -step), (0, step),
                      (-step, -step), (-step, step), (step, -step), (step, step)]
    elif is_center((moved_piece.x, moved_piece.y)):
        step = 0.5  # Only 4 diagonal directions for center positions
        directions = [(-step, -step), (-step, step), (step, -step), (step, step)]
    else:
        return  # Invalid position

    for dx, dy in directions:
        x, y = moved_piece.x, moved_piece.y
        pieces_to_flip = []
        while True:
            x += dx
            y += dy
            if not (0 <= x <= 4 and 0 <= y <= 4):  # Reached the edge of the board
                break
            current_piece = get_piece_at_pos(pieces, (x, y))
            if current_piece is None:  # Empty space, no capture
                break
            elif current_piece.color != moved_piece.color:  # Enemy piece, add to list to flip
                pieces_to_flip.append(current_piece)
            else:  # Found own piece, capture occurs
                if pieces_to_flip:  # Flip all enemy pieces in this direction
                    for piece in pieces_to_flip:
                        piece.flip()
                break  # Stop checking this direction


def main():
    clock = pygame.time.Clock()
    pieces = create_pieces()
    selected_piece = None
    valid_moves = []
    run = True
    # Add a variable to keep track of whose turn it is
    turn = 'green'  # Green pieces go first

    while run:
        clock.tick(60)  # Set the frame rate to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_pos = get_clicked_pos(mouse_pos)
                piece = get_piece_at_pos(pieces, clicked_pos)

                if selected_piece:
                    # Try to move to clicked position
                    if clicked_pos in valid_moves:
                        # Move the piece
                        selected_piece.move(clicked_pos[0], clicked_pos[1])
                        selected_piece.selected = False
                        # Perform capturing
                        capture_pieces(pieces, selected_piece)
                        selected_piece = None
                        valid_moves = []
                        # Switch turn after a successful move
                        turn = 'yellow' if turn == 'green' else 'green'
                    else:
                        selected_piece.selected = False
                        selected_piece = None
                        valid_moves = []
                elif piece:
                    # Only allow selection if the piece belongs to the current player
                    if piece.color == turn:
                        selected_piece = piece
                        selected_piece.selected = True
                        valid_moves = get_valid_moves(selected_piece, pieces)
                else:
                    # Optionally, provide feedback that it's not this player's turn
                    print(f"It's {turn}'s turn.")

        draw_board(WIN, pieces)

        # Highlight valid moves
        for move in valid_moves:
            blit_x, blit_y = get_blit_pos(move)
            pygame.draw.circle(WIN, HIGHLIGHT_COLOR,
                               (blit_x + scaled_size // 2, blit_y + scaled_size // 2), scaled_size // 2 + 5, 2)

        # Display turn information
        font = pygame.font.SysFont(None, 36)
        turn_text = font.render(f"{turn.capitalize()}'s Turn", True, BLACK)
        WIN.blit(turn_text, (10, 10))

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()