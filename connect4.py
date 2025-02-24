import numpy as np
import random
import math

ROWS = 6
COLS = 7
PLAYER = 1
AI = 2

EMPTY = 0
WINDOW_LENGTH = 4

def create_board():
    return np.zeros((ROWS, COLS), dtype=int)

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            return r
    return -1

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def winning_move(board, piece):
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r, c+i] == piece for i in range(4)):
                return True
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(board[r+i, c] == piece for i in range(4)):
                return True
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i, c+i] == piece for i in range(4)):
                return True
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i, c+i] == piece for i in range(4)):
                return True
    return False

def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_location(board, col)]

def evaluate_window(window, piece):
    """Assigns a score to a given sequence of four slots."""
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 50  # High penalty for letting opponent win

    return score

def score_position(board, piece):
    """Scores the current board position to help AI decide on moves."""
    score = 0

    # Prioritize center column (strategic advantage)
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # Score Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Positive Slope Diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score Negative Slope Diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    """Checks if the game is over (win or draw)."""
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    """Minimax algorithm with Alpha-Beta pruning for AI decision-making."""
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, 1000000)
            elif winning_move(board, PLAYER):
                return (None, -1000000)
            else:  # Draw
                return (None, 0)
        else:
            return (None, score_position(board, AI))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI)
            new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER)
            new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value



def get_ai_move(board, depth=5):
    """Uses Minimax algorithm to determine the AI's best move."""
    import math
    col, _ = minimax(board, depth, -math.inf, math.inf, True)
    return col



def get_winning_combination(board, piece):
    # Check horizontal locations for win
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = board[r, c:c+4]
            if all(slot == piece for slot in window):
                return [(r, c + i) for i in range(4)]

    # Check vertical locations for win
    for r in range(ROWS - 3):
        for c in range(COLS):
            window = board[r:r+4, c]
            if all(slot == piece for slot in window):
                return [(r + i, c) for i in range(4)]

    # Check positively sloped diagonals
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r+1][c+1] == piece and
                board[r+2][c+2] == piece and
                board[r+3][c+3] == piece):
                return [(r + i, c + i) for i in range(4)]

    # Check negatively sloped diagonals
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if (board[r][c] == piece and
                board[r-1][c+1] == piece and
                board[r-2][c+2] == piece and
                board[r-3][c+3] == piece):
                return [(r - i, c + i) for i in range(4)]

    return None


