from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import connect4
import os

app = Flask(__name__, static_folder="static")
CORS(app)

board = connect4.create_board()
current_player = 1

# New global variable for AI depth
current_depth = 5  # default to 'medium' if you like

def reset_board():
    global board, current_player
    board = connect4.create_board()
    current_player = 1

@app.route('/')
def serve_frontend():
    return send_from_directory("static", "index.html")


@app.route('/set_difficulty', methods=['POST'])
def set_difficulty():
    """
    Receives JSON data like {"depth": 4} from the frontend 
    and sets a global difficulty value for the AI.
    """
    global current_depth
    data = request.json
    if 'depth' not in data:
        return jsonify({'error': 'Missing depth'}), 400

    current_depth = data['depth']
    return jsonify({'status': 'ok', 'depth': current_depth})

@app.route('/move', methods=['POST'])
def make_move():
    global board, current_depth
    data = request.json
    
    # If AI move is requested
    if 'column' in data and data['column'] == -1:
        ai_col = connect4.get_ai_move(board, depth=current_depth)
        if ai_col is not None and connect4.is_valid_location(board, ai_col):
            ai_row = connect4.get_next_open_row(board, ai_col)
            connect4.drop_piece(board, ai_row, ai_col, 2)
            # Check AI win
            winning_cells = connect4.get_winning_combination(board, 2)
            if winning_cells:
                return jsonify({
                    'status': 'win',
                    'board': board.tolist(),
                    'winner': 2,
                    'winningCells': winning_cells
                })
        return jsonify({
            'status': 'continue',
            'board': board.tolist()
        })

    # Otherwise, handle player's move
    if 'column' not in data:
        return jsonify({'error': 'Missing column data'}), 400
    
    column = data['column']
    if not connect4.is_valid_location(board, column):
        return jsonify({'status': 'invalid move'}), 400

    row = connect4.get_next_open_row(board, column)
    connect4.drop_piece(board, row, column, 1)

    winning_cells = connect4.get_winning_combination(board, 1)
    if winning_cells:
        return jsonify({
            'status': 'win',
            'board': board.tolist(),
            'winner': 1,
            'winningCells': winning_cells
        })

    return jsonify({
        'status': 'continue',
        'board': board.tolist()
    })

@app.route('/restart', methods=['POST'])
def restart_game():
    reset_board()
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)
