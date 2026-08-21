import sudoku_logic


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