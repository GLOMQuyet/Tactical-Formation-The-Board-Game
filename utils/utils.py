
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

