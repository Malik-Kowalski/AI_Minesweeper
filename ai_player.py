import random
from neighbour_deduction import NeighbourDeduction


class AIPlayer:
    def __init__(self, game):
        self.game = game
        self.neighbour_deduction = NeighbourDeduction(game)

    def make_move(self):
        safe_move = self.neighbour_deduction.find_safe_move()
        if safe_move:
            print("AI znalazło bezpieczny ruch")
            return safe_move

        print("Brak bezpiecznego ruchu, AI wykonuje losowy ruch.")
        random_move = self.get_random_move()
        return random_move

    def get_random_move(self):
        available_moves = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col] and not self.game.flags[row][col]:
                    available_moves.append((row, col))

        if available_moves:
            return random.choice(available_moves)
        return None
