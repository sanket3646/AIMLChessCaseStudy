#
# Web based GUI for BBC chess engine
#
import os
import sys

# packages
from flask import Flask
from flask import render_template
from flask import request
import chess
import chess.engine
import chess.pgn
import io
import random
from flask import jsonify
from flask import Response
from flask_pymongo import PyMongo
from datetime import datetime
import json

# create web app instance
app = Flask(__name__)

# probe book move
def probe_book(pgn):
    # open book file
    with open('./engine/book.txt') as f:
        # read book games
        book = f.read()

        # init board        
        board = chess.Board()
        
        # define response moves
        response_moves = []

        # loop over book lines
        for line in book.split('\n')[0:-1]:
            # define variation
            variation = []
            
            # loop over line moves
            for move in line.split():
                variation.append(chess.Move.from_uci(move))
            
            # parse variation to SAN
            san = board.variation_san(variation)
            
            # match book line line
            if pgn in san:
                try:
                    # black move
                    if san.split(pgn)[-1].split()[0][0].isdigit():
                        response_moves.append(san.split(pgn)[-1].split()[1])
                    
                    # white move
                    else:
                        response_moves.append(san.split(pgn)[-1].split()[0])
                
                except:
                    pass
            
            # engine makes first move
            if pgn == '':
                response_moves.append(san.split('1. ')[-1].split()[0])

        # return random response move
        if len(response_moves):
            print('BOOK MOVE:', random.choice(response_moves))
            return random.choice(response_moves)
        
        else:
            return 0

# root(index) route
@app.route('/')
def root():
    return render_template('bbc.html')

# make move API
@app.route('/make_move', methods=['POST'])
def make_move():
    # extract FEN string from HTTP POST request body
    pgn = request.form.get('pgn')
    
    # probe opening book
    """
    if probe_book(pgn):
        return {
            'score': 'book move',
            'best_move': probe_book(pgn)
        }
    """
    # read game moves from PGN
    game = chess.pgn.read_game(io.StringIO(pgn))    
    
    # init board
    board = game.board()
    
    # loop over moves in game
    for move in game.mainline_moves():
        # make move on chess board
        board.push(move)
    
    # create chess engine instance
    engine_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "mini-stockfish")
)

    engine = chess.engine.SimpleEngine.popen_uci(
        [sys.executable, os.path.join(engine_dir, "uci_engine.py")],
        cwd=engine_dir,
    ) 
    # extract fixed depth value
    
    fixed_depth = request.form.get('fixed_depth', '0')
    move_time = request.form.get('move_time', '0')

    try:
        if fixed_depth != '0':
            info = engine.analyse(
                board,
                chess.engine.Limit(depth=int(fixed_depth))
            )
        elif move_time == 'instant':
            info = engine.analyse(
                board,
                chess.engine.Limit(time=0.1)
            )
        elif move_time != '0':
            info = engine.analyse(
                board,
                chess.engine.Limit(time=int(move_time))
            )
        else:
            return {'error': 'No search limit selected'}, 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f'Engine analysis failed: {e}'}, 500

    finally:
        engine.quit()

    print("DEBUG INFO:", info, flush=True)

    
    try:
        # extract best move from PV
        pv = info.get('pv', [])

        if not pv:
            print("ERROR: No PV returned", flush=True)
            print("INFO:", info, flush=True)
            return {
                'error': 'Engine returned no principal variation',
                'score': str(info.get('score', 'Unknown')),
                'fen': board.fen()
            }, 500

        best_move = pv[0]

        # update internal python chess board state
        board.push(best_move)
        
       
        
        # get best score
        try:
            score = -int(str(info['score'])) / 100
        
        except:
            score = str(info['score'])
            
            # inverse score
            if '+' in score:
                score = score.replace('+', '-')
            
            elif '-' in score:
                score = score.replace('-', '+')
          
        return {
            'fen': board.fen(),
            'best_move': str(best_move),
            'score': score,
            'depth': info['depth'],
            'pv': ' '.join([str(move) for move in info['pv']]),
            'nodes': info['nodes'],
            'time': info['time']
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'errror': str(e)}, 500
        

@app.route('/analytics')
def analytics():
    return render_template('stats.html')

@app.route('/analytics/api/post', methods=['POST'])
def post():
    response = Response('')
    response.headers['Access-Control-Allow-Origin'] = '*'

    stats = {
        'Date': request.form.get('date'),
        'Url': request.form.get('url'),
        'Agent':request.headers.get('User-Agent')
    }

    if request.headers.getlist("X-Forwarded-For"):
       stats['Ip'] = request.headers.getlist("X-Forwarded-For")[0]
    else:
       stats['Ip'] = request.remote_addr
    
    if request.headers.get('Origin'):
        stats['Origin'] = request.headers.get('Origin')
    else:
        stats['Origin'] = 'N/A'
    
    if request.headers.get('Referer'):
        stats['Referer'] = request.headers.get('Referer')
    else:
        stats['Referer'] = 'N/A'
    
    with open('stats.json', 'a') as f: f.write(json.dumps(stats, indent=2) + '\n\n')
    return response


@app.route('/analytics/api/get')
def get():
    stats = []
    
    with open('stats.json') as f:
        for entry in f.read().split('\n\n'):
            try: stats.append(json.loads(entry))
            except: pass
              
    return jsonify({'data': stats})

# main driver
if __name__ == '__main__':
    # start HTTP server
    app.run(debug=True, threaded=True)
