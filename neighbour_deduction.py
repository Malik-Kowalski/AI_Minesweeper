class NeighbourDeduction:
    def __init__(self, game):
        self.game = game

    def find_safe_move(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.revealed[row][col]:
                    continue
                if self.is_safe(row, col):
                    return (row, col)
        return None

    def is_safe(self, row, col):
        return self.game.board[row][col] == 0

    def get_neighbours(self, row, col):
        neighbours = []
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (r == row and c == col) or not self.is_valid(r, c):
                    continue
                neighbours.append((r, c))
        return neighbours

    def is_valid(self, row, col):
        return 0 <= row < self.game.rows and 0 <= col < self.game.cols
