import random
from collections import defaultdict

class MonteCarloAnalyzer:
    def __init__(self, game):
        self.game = game

    def analyze(self, iterations=1000):
        scores = defaultdict(int)

        for _ in range(iterations):
            simulated_board = self._simulate_board()

            for row in range(self.game.rows):
                for col in range(self.game.cols):
                    if not self.game.revealed[row][col] and not self.game.flags[row][col]:
                        if simulated_board[row][col] == -1:
                            scores[(row, col)] += 1

        min_risk = float('inf')
        best_move = None
        for (row, col), risk in scores.items():
            if risk < min_risk:
                min_risk = risk
                best_move = (row, col)

        print("=== Wyniki Monte Carlo ===")
        for (row, col), risk in scores.items():
            print(f"Pole ({row}, {col}): Ryzyko = {risk / iterations:.2%}")
        print(f"Wybrane pole: {best_move} z ryzykiem {min_risk / iterations:.2%}")

        return best_move

    def _simulate_board(self):
        simulated_board = [[0 for _ in range(self.game.cols)] for _ in range(self.game.rows)]

        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.revealed[row][col]:
                    simulated_board[row][col] = self.game.board[row][col]

        remaining_mines = self.game.mines - sum(
            row.count(-1) for row in simulated_board
        )
        while remaining_mines > 0:
            row = random.randint(0, self.game.rows - 1)
            col = random.randint(0, self.game.cols - 1)
            if not self.game.revealed[row][col] and simulated_board[row][col] != -1:
                simulated_board[row][col] = -1
                remaining_mines -= 1

        return simulated_board
