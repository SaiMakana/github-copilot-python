import sudoku_logic


VALID_COMPLETED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(row == [sudoku_logic.EMPTY] * sudoku_logic.SIZE for row in board)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 1, 1, 6)


def test_fill_board_produces_valid_completed_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board)
    assert all(1 <= cell <= sudoku_logic.SIZE for row in board for cell in row)
    for row in board:
        assert len(set(row)) == sudoku_logic.SIZE
    for column in zip(*board):
        assert len(set(column)) == sudoku_logic.SIZE


def test_generate_puzzle_preserves_solution_and_requested_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=81)

    assert puzzle == solution
    assert all(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)


def test_generated_puzzle_has_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sudoku_logic.count_solutions(solution) == 1


def test_generated_solution_solves_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_generated_puzzle_respects_requested_clue_count():
    puzzle, _ = sudoku_logic.generate_puzzle(clues=40)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40


def test_generate_puzzle_rejects_invalid_clue_counts():
    for clues in (-1, sudoku_logic.SIZE * sudoku_logic.SIZE + 1):
        try:
            sudoku_logic.generate_puzzle(clues)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid clue count was accepted')

    for clues in (35.0, '35', True):
        try:
            sudoku_logic.generate_puzzle(clues)
        except TypeError:
            pass
        else:
            raise AssertionError('non-integer clue count was accepted')


def test_count_solutions_returns_one_for_completed_valid_board():
    assert sudoku_logic.count_solutions(VALID_COMPLETED_BOARD) == 1


def test_count_solutions_returns_zero_for_contradictory_board():
    board = sudoku_logic.deep_copy(VALID_COMPLETED_BOARD)
    board[0][1] = board[0][0]

    assert sudoku_logic.count_solutions(board) == 0


def test_count_solutions_stops_at_two_for_board_with_multiple_solutions():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board, limit=2) == 2


def test_count_solutions_does_not_modify_input_board():
    board = sudoku_logic.deep_copy(VALID_COMPLETED_BOARD)
    board[0][0] = sudoku_logic.EMPTY
    original = sudoku_logic.deep_copy(board)

    sudoku_logic.count_solutions(board)

    assert board == original