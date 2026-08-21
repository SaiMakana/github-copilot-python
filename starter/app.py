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
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)