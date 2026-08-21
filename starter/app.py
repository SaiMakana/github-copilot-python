from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 28,
}

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


def is_valid_board(board):
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(
            isinstance(row, list) and len(row) == sudoku_logic.SIZE
            for row in board
        )
        and all(
            not isinstance(cell, bool)
            and isinstance(cell, int)
            and sudoku_logic.EMPTY <= cell <= sudoku_logic.SIZE
            for row in board
            for cell in row
        )
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty_value = request.args.get('difficulty')
    if difficulty_value is not None:
        difficulty = difficulty_value.lower()
        clues = DIFFICULTY_CLUES.get(difficulty)
        if clues is None:
            return jsonify({'error': 'Difficulty must be easy, medium, or hard'}), 400
    else:
        clues_value = request.args.get('clues')
        difficulty = None
        if clues_value is None:
            difficulty = 'medium'
            clues = DIFFICULTY_CLUES[difficulty]
        else:
            try:
                clues = int(clues_value)
            except (TypeError, ValueError):
                return jsonify({'error': 'clues must be an integer'}), 400
            if clues < 0 or clues > sudoku_logic.SIZE * sudoku_logic.SIZE:
                return jsonify({'error': 'clues must be between 0 and 81'}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or 'board' not in data:
        return jsonify({'error': 'board is required'}), 400

    board = data['board']
    if not is_valid_board(board):
        return jsonify({'error': 'board must be a 9x9 grid of values from 0 to 9'}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def provide_hint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or 'board' not in data:
        return jsonify({'error': 'board is required'}), 400

    board = data['board']
    if not is_valid_board(board):
        return jsonify({'error': 'board must be a 9x9 grid of values from 0 to 9'}), 400

    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY:
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                })

    return jsonify({'hint': None, 'message': 'No empty cells left'})

if __name__ == '__main__':
    app.run(debug=True)