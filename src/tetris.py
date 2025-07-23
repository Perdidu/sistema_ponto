"""
Simple Tetris clone using curses.
Use arrow keys to move, up to rotate and q to quit.
"""

import curses
import random
import time

# Tetromino shapes in rotation states
SHAPES = {
    'I': [[(0,1),(1,1),(2,1),(3,1)], [(2,0),(2,1),(2,2),(2,3)]],
    'J': [[(0,0),(0,1),(1,1),(2,1)], [(1,0),(2,0),(1,1),(1,2)],
          [(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(0,2),(1,2)]],
    'L': [[(2,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(1,2),(2,2)],
          [(0,1),(1,1),(2,1),(0,2)], [(0,0),(1,0),(1,1),(1,2)]],
    'O': [[(1,0),(2,0),(1,1),(2,1)]],
    'S': [[(1,0),(2,0),(0,1),(1,1)], [(1,0),(1,1),(2,1),(2,2)]],
    'T': [[(1,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(2,1),(1,2)],
          [(0,1),(1,1),(2,1),(1,2)], [(1,0),(0,1),(1,1),(1,2)]],
    'Z': [[(0,0),(1,0),(1,1),(2,1)], [(2,0),(1,1),(2,1),(1,2)]]
}

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rot = 0
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0

    @property
    def cells(self):
        return SHAPES[self.shape][self.rot]

    def rotate(self, board):
        new_rot = (self.rot + 1) % len(SHAPES[self.shape])
        if not self._collision(board, self.x, self.y, new_rot):
            self.rot = new_rot

    def move(self, dx, dy, board):
        if not self._collision(board, self.x + dx, self.y + dy, self.rot):
            self.x += dx
            self.y += dy
            return True
        return False

    def _collision(self, board, x, y, rot):
        for cx, cy in SHAPES[self.shape][rot]:
            px = x + cx
            py = y + cy
            if px < 0 or px >= BOARD_WIDTH or py < 0 or py >= BOARD_HEIGHT:
                return True
            if board[py][px]:
                return True
        return False

    def imprint(self, board):
        for cx, cy in self.cells:
            board[self.y + cy][self.x + cx] = self.shape


def new_board():
    return [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def remove_complete_lines(board):
    new_board_rows = [row for row in board if any(cell is None for cell in row)]
    removed = BOARD_HEIGHT - len(new_board_rows)
    for _ in range(removed):
        new_board_rows.insert(0, [None for _ in range(BOARD_WIDTH)])
    return new_board_rows, removed


def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            char = '[]' if board[y][x] else '  '
            stdscr.addstr(y, x * 2, char)
    if piece:
        for cx, cy in piece.cells:
            px = piece.x + cx
            py = piece.y + cy
            if 0 <= px < BOARD_WIDTH and 0 <= py < BOARD_HEIGHT:
                stdscr.addstr(py, px * 2, '[]')
    stdscr.addstr(0, BOARD_WIDTH * 2 + 2, f'Score: {score}')
    stdscr.refresh()


def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    board = new_board()
    piece = Piece(random.choice(list(SHAPES.keys())))
    score = 0
    last_fall = time.time()
    delay = 0.5

    while True:
        draw_board(stdscr, board, piece, score)
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            piece.move(-1, 0, board)
        elif key == curses.KEY_RIGHT:
            piece.move(1, 0, board)
        elif key == curses.KEY_DOWN:
            if not piece.move(0, 1, board):
                piece.imprint(board)
                board, removed = remove_complete_lines(board)
                score += removed * 100
                piece = Piece(random.choice(list(SHAPES.keys())))
                if piece._collision(board, piece.x, piece.y, piece.rot):
                    break
        elif key == curses.KEY_UP:
            piece.rotate(board)
        elif key == ord('q'):
            break

        if time.time() - last_fall > delay:
            if not piece.move(0, 1, board):
                piece.imprint(board)
                board, removed = remove_complete_lines(board)
                score += removed * 100
                piece = Piece(random.choice(list(SHAPES.keys())))
                if piece._collision(board, piece.x, piece.y, piece.rot):
                    break
            last_fall = time.time()

    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH - 4, 'Game Over!')
    stdscr.addstr(BOARD_HEIGHT // 2 + 1, BOARD_WIDTH - 6, f'Score: {score}')
    stdscr.addstr(BOARD_HEIGHT // 2 + 2, BOARD_WIDTH - 10, 'Press any key')
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(game_loop)
