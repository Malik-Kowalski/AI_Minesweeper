class NeighbourDeduction:
    def __init__(self, game):
        self.game = game

    def find_move(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col]:
                    continue

                mine_count = self.game.board[row][col]
                neighbours = self.get_neighbours(row, col)

                hidden_neighbours = [n for n in neighbours if not self.game.revealed[n[0]][n[1]]]
                flagged_neighbours = [n for n in neighbours if self.game.flags[n[0]][n[1]]]

                if len(flagged_neighbours) == mine_count:
                    for n in hidden_neighbours:
                        if not self.game.flags[n[0]][n[1]]:
                            return ('reveal', n[0], n[1])

                remaining_mines = mine_count - len(flagged_neighbours)
                if remaining_mines > 0 and len(hidden_neighbours) == remaining_mines:
                    for n in hidden_neighbours:
                        if not self.game.flags[n[0]][n[1]]:
                            return ('flag', n[0], n[1])

        return None

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
