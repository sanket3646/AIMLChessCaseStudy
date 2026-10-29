
import chess
import time

from engine.search import find_best_move_alpha_beta

DEPTH = 4


def get_human_move(board):
    while True:
        move_text = input("Your move (e.g. e2e4): ").strip()

        try:
            move = chess.Move.from_uci(move_text)
        except ValueError:
            print("Invalid format. Try something like e2e4.")
            continue

        if move in board.legal_moves:
            return move

        print("Illegal move. Try again.")


def main():
    board = chess.Board()

    print("Mini-Stockfish: You are White; the bot is Black.")
    print("Enter moves in UCI format, such as e2e4 or g1f3.")
    print("Type 'quit' to stop playing.")

    while not board.is_game_over():
        print("\n")
        print(board,"\n")

        if board.turn == chess.WHITE:
            move_text = input("Your move: ").strip()

            if move_text.lower() == "quit":
                print("Game stopped.")
                return

            try:
                move = chess.Move.from_uci(move_text)
            except ValueError:
                print("Invalid format.")
                continue

            if move not in board.legal_moves:
                print("Illegal move.")
                continue

        else:
            print("Bot is thinking...")
            start = time.perf_counter()

            move, score = find_best_move_alpha_beta(
                board, DEPTH
            )

            elapsed = time.perf_counter() - start
            print(
                f"Bot plays {board.san(move)} "
                f"({move.uci()}) | "
                f"Score: {score} | "
                f"Time: {elapsed:.2f}s"
            )

        board.push(move)

    print("\nFinal position:\n", board)
    print("\nGame over:", board.result())
    print(board.outcome())


if __name__ == "__main__":
    main()
