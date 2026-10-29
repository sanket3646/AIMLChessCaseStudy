

import sys
import chess

from engine.search import find_best_move_alpha_beta


def send(message):
    print(message, flush=True)


def main():
    board = chess.Board()
    send("id name Mini-Stockfish")
    print(">>> MY MINI-STOCKFISH ENGINE STARTED <<<", file=sys.stderr, flush=True)
    # Wait for the GUI to send UCI commands.
    # Only protocol responses are printed to stdout.

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        parts = line.strip().split()
        if not parts:
            continue

        command = parts[0]

        if command == "uci":
            send("id name Mini-Stockfish")
            send("id author Sanket")
            send("uciok")

        elif command == "isready":
            send("readyok")

        elif command == "ucinewgame":
            board = chess.Board()

        elif command == "position":
            try:
                if parts[1] == "startpos":
                    board = chess.Board()
                    moves_index = 2
                elif parts[1] == "fen":
                    moves_index = (
                        parts.index("moves")
                        if "moves" in parts
                        else len(parts)
                    )
                    board = chess.Board(
                        " ".join(parts[2:moves_index])
                    )
                else:
                    continue

                if "moves" in parts[moves_index:]:
                    start = parts.index("moves", moves_index) + 1
                    for move_text in parts[start:]:
                        board.push_uci(move_text)

            except (ValueError, IndexError):
                continue

        elif command == "go":
            if board.is_game_over():
                send("bestmove 0000")
                continue

            depth = 4
            if "depth" in parts:
                try:
                    depth = int(parts[parts.index("depth") + 1])
                except (ValueError, IndexError):
                    pass

            # Time-based requests use a modest default depth for now.
            # We will add proper time-managed search later.
            depth = max(1, min(depth, 5))

            move, score = find_best_move_alpha_beta(
                board, depth
            )

            if move is None:
                send("bestmove 0000")
            else:
                score = score if board.turn == chess.WHITE else -score
                send(
                    f"info depth {depth} time 1 nodes 1 "
                    f"score cp {score} pv {move.uci()}"
                )                
                send(f"bestmove {move.uci()}")

        elif command == "stop":
            # Current searches finish synchronously.
            pass

        elif command == "quit":
            break


if __name__ == "__main__":
    main()
