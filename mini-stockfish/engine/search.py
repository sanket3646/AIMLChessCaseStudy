import chess
from engine.evaluation import evaluate_position
board = chess.Board()
def minimax(board, depth, maximizing_player):

    #stop searching when depth reached or game over
    if depth == 0 or board.is_game_over():
        return evaluate_position(board)

    if maximizing_player:
        best_score = float("-inf")

        for move in board.legal_moves:
            board.push(move)

            score = minimax(board, depth-1, False)
            board.pop()
            best_score = max(score, best_score)

        return best_score

    else:
        best_score = float("inf")

        for move in board.legal_moves:
            board.push(move)

            score = minimax(board, depth-1, True)
            board.pop()
            best_score = min(score, best_score)

        return best_score

def find_best_move(board, depth):
    maximizing_player = board.turn == chess.WHITE

    best_move = None

    if maximizing_player:
        best_score = float("-inf")
    else:
        best_score = float("inf")

    for move in board.legal_moves:
        board.push(move)

        score = minimax(board, depth-1, not maximizing_player)
        board.pop()

        if maximizing_player and score>best_score:
            best_score = score
            best_move  = move

        elif not maximizing_player and score<best_score:
            best_score = score
            best_move = move

    return best_move, best_score





def quiescence(board, alpha, beta, maximizing_player, qdepth=0):
    if board.is_game_over():
        return evaluate_position(board)

    in_check = board.is_check()

    # Prevent excessively long capture sequences.
    if qdepth >= 8 and not in_check:
        return evaluate_position(board)

    if not in_check:
        stand_pat = evaluate_position(board)

        if maximizing_player:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

        best_score = stand_pat
        moves = [
            move for move in board.legal_moves
            if board.is_capture(move)
        ]
    else:
        # In check, stand-pat is illegal: search evasions.
        best_score = (
            float("-inf")
            if maximizing_player
            else float("inf")
        )
        moves = list(board.legal_moves)

        if not moves:
            return evaluate_position(board)

    for move in moves:
        board.push(move)
        score = quiescence(
            board, alpha, beta, not maximizing_player, qdepth + 1
        )
        board.pop()

        if maximizing_player:
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
        else:
            best_score = min(best_score, score)
            beta = min(beta, best_score)

        if alpha >= beta:
            break

    return best_score



def alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth ==0 or board.is_game_over():
        return evaluate_position(board)

    if depth == 0:
        return quiescence(board, alpha, beta, maximizing_player)
    
    if maximizing_player:
        best_score = float("-inf")

        for move in board.legal_moves:
            board.push(move)
            score = alpha_beta(
                board, depth - 1, alpha, beta, False
            )
            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in board.legal_moves:
            board.push(move)
            score = alpha_beta(
                board, depth - 1, alpha, beta, True
            )
            board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if alpha >= beta:
                break

        return best_score


def find_best_move_alpha_beta(board, depth):
    maximizing_player = board.turn == chess.WHITE

    best_move = None
    alpha = float("-inf")
    beta = float("inf")

    if maximizing_player:
        best_score = float("-inf")
    else:
        best_score = float("inf")

    for move in board.legal_moves:
        board.push(move)

        score = alpha_beta(
            board,
            depth - 1,
            alpha,
            beta,
            not maximizing_player
        )

        board.pop()

        if maximizing_player and score > best_score:
            best_score = score
            best_move = move
            alpha = max(alpha, best_score)

        elif not maximizing_player and score < best_score:
            best_score = score
            best_move = move
            beta = min(beta, best_score)

    return best_move, best_score
