import random
class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flags = [[False for _ in range(cols)] for _ in range(rows)]
        self._place_mines()
        self._calculate_numbers()

    def _place_mines(self):
        placed_mines = 0
        while placed_mines < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.board[row][col] == 0:
                self.board[row][col] = -1
                placed_mines += 1

    def reveal(self, row, col):
        if self.revealed[row][col] or self.flags[row][col]:
            return
        self.revealed[row][col] = True
        if self.board[row][col] == -1:
            return "game_over"
        elif self.board[row][col] == 0:
            self._reveal_neighbors(row, col)
        if self.check_win():
            return "win"
        return "safe"

    def flag(self, row, col):
        if not self.revealed[row][col]:
            self.flags[row][col] = not self.flags[row][col]

    def _reveal_neighbors(self, row, col):
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if 0 <= r < self.rows and 0 <= c < self.cols and not self.revealed[r][c]:
                    self.reveal(r, c)

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1 and not self.revealed[row][col]:
                    return False
        return True

    def _calculate_numbers(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == -1:
                    continue
                mine_count = 0
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == -1:
                            mine_count += 1
                self.board[row][col] = mine_count

