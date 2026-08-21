import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def count_solutions(board, limit=2):
    if limit <= 0:
        return 0

    working_board = deep_copy(board)
    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if value == EMPTY:
                continue
            if value < 1 or value > SIZE:
                return 0
            working_board[row][col] = EMPTY
            if not is_safe(working_board, row, col, value):
                return 0
            working_board[row][col] = value

    def count_from_current_board():
        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue
                solutions = 0
                for candidate in range(1, SIZE + 1):
                    if is_safe(working_board, row, col, candidate):
                        working_board[row][col] = candidate
                        solutions += count_from_current_board()
                        working_board[row][col] = EMPTY
                        if solutions >= limit:
                            return limit
                return solutions
        return 1

    return count_from_current_board()

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    coordinates = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(coordinates)
    filled_cells = SIZE * SIZE

    for row, col in coordinates:
        if filled_cells <= clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) == 1:
            filled_cells -= 1
        else:
            board[row][col] = value

def generate_puzzle(clues=35):
    if isinstance(clues, bool) or not isinstance(clues, int):
        raise TypeError('clues must be an integer')
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError(f'clues must be between 0 and {SIZE * SIZE}')

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
