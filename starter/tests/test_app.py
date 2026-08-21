import sudoku_logic

import app


def count_clues(board):
    return sum(
        cell != sudoku_logic.EMPTY
        for row in board
        for cell in row
    )


def test_index_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_game_returns_nine_by_nine_puzzle(client):
    response = client.get('/new?clues=81')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(1 <= cell <= sudoku_logic.SIZE for row in puzzle for cell in row)
    assert app.CURRENT['puzzle'] == puzzle
    assert app.CURRENT['solution'] is not None


def test_new_defaults_to_medium_difficulty(client):
    response = client.get('/new')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'medium'
    assert count_clues(data['puzzle']) == 35


def test_new_supports_easy_difficulty(client):
    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'easy'
    assert count_clues(data['puzzle']) == 45


def test_new_supports_medium_difficulty(client):
    response = client.get('/new?difficulty=medium')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'medium'
    assert count_clues(data['puzzle']) == 35


def test_new_supports_hard_difficulty(client):
    response = client.get('/new?difficulty=hard')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'hard'
    assert count_clues(data['puzzle']) == 28


def test_new_difficulty_is_case_insensitive(client):
    response = client.get('/new?difficulty=HARD')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'hard'
    assert count_clues(data['puzzle']) == 28


def test_new_rejects_invalid_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'Difficulty must be easy, medium, or hard'
    }


def test_legacy_clues_parameter_remains_supported(client):
    response = client.get('/new?clues=40')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] is None
    assert count_clues(data['puzzle']) == 40


def test_legacy_complete_board_remains_supported(client):
    response = client.get('/new?clues=81')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] is None
    assert count_clues(data['puzzle']) == 81


def test_new_rejects_invalid_legacy_clues(client):
    for clues in ('not-a-number', '-1', '82'):
        response = client.get(f'/new?clues={clues}')

        assert response.status_code == 400
        assert response.get_json() == {
            'error': 'clues must be an integer'
        } if clues == 'not-a-number' else {
            'error': 'clues must be between 0 and 81'
        }


def test_difficulty_takes_precedence_over_legacy_clues(client):
    response = client.get('/new?difficulty=hard&clues=81')

    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'hard'
    assert count_clues(data['puzzle']) == 28


def test_check_requires_game_in_progress(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_marks_incorrect_cells(client):
    client.get('/new?clues=81')
    board = sudoku_logic.deep_copy(app.CURRENT['solution'])
    board[0][0] = 1 if board[0][0] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_marks_multiple_incorrect_cells(client):
    client.get('/new?clues=81')
    board = sudoku_logic.deep_copy(app.CURRENT['solution'])
    board[0][0] = 1 if board[0][0] != 1 else 2
    board[1][1] = 1 if board[1][1] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0], [1, 1]]}


def test_check_marks_incomplete_board(client):
    client.get('/new?clues=81')
    board = sudoku_logic.deep_copy(app.CURRENT['solution'])
    board[0][0] = sudoku_logic.EMPTY

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_accepts_current_solution(client):
    client.get('/new?clues=81')

    response = client.post('/check', json={'board': app.CURRENT['solution']})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_rejects_missing_board(client):
    client.get('/new?clues=81')

    response = client.post('/check', json={})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'board is required'}


def test_check_rejects_malformed_board(client):
    client.get('/new?clues=81')

    response = client.post('/check', json={'board': [[0]]})

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'board must be a 9x9 grid of values from 0 to 9'
    }


def test_check_rejects_invalid_cell_values(client):
    client.get('/new?clues=81')
    board = sudoku_logic.create_empty_board()
    board[0][0] = 10

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'board must be a 9x9 grid of values from 0 to 9'
    }