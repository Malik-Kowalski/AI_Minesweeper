class NeighbourDeduction:
    def __init__(self, game):
        self.game = game

    def find_move(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col]:
                    continue

                mine_count = self.game.board[row][col]
                neighbours = self._get_neighbours(row, col)

                hidden_neighbours = [n for n in neighbours if not self.game.revealed[n[0]][n[1]]]
                flagged_neighbours = [n for n in neighbours if self.game.flags[n[0]][n[1]]]
                if len(flagged_neighbours) < mine_count:
                    continue
                if len(flagged_neighbours) == mine_count and len(hidden_neighbours) > 0:
                    print(
                        f"Pole ({row}, {col}) -> miny: {mine_count}, ukryte: {len(hidden_neighbours)}, flagi: {len(flagged_neighbours)}"
                    )
                    for n in hidden_neighbours:
                        if not self.game.flags[n[0]][n[1]]:
                            return ('reveal', n[0], n[1])

        return None

    def _get_neighbours(self, row, col):
        neighbours = []
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if (r == row and c == col) or not self._is_valid(r, c):
                    continue
                neighbours.append((r, c))
        return neighbours

    def _is_valid(self, row, col):
        return 0 <= row < self.game.rows and 0 <= col < self.game.cols
