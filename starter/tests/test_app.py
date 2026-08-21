import sudoku_logic

import app


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


def test_check_accepts_current_solution(client):
    client.get('/new?clues=81')

    response = client.post('/check', json={'board': app.CURRENT['solution']})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}