
import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Bonus for a piece's position, indexed by rank from White's side.
# These are simple handcrafted heuristics, not trained parameters.
PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]


def evaluate_position(board):
    # Handle checkmate and draws first.
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -100000
        return 100000

    if board.is_game_over():
        return 0

    score = 0

    for color in (chess.WHITE, chess.BLACK):
        sign = 1 if color == chess.WHITE else -1

        for piece_type, value in PIECE_VALUES.items():
            for square in board.pieces(piece_type, color):
                # Material value
                score += sign * value

                # Add positional bonuses for pawns and knights.
                # python-chess numbers a1 as 0 and h8 as 63.
                table_index = (
                    chess.square_mirror(square)
                    if color == chess.BLACK
                    else square
                )

                if piece_type == chess.PAWN:
                    score += sign * PAWN_TABLE[table_index]

                elif piece_type == chess.KNIGHT:
                    score += sign * KNIGHT_TABLE[table_index]

    return score
