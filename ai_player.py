import random
from neighbour_deduction import NeighbourDeduction

class AIPlayer:
    def __init__(self, game):
        self.game = game
        self.neighbour_deduction = NeighbourDeduction(game)

    def make_move(self):

        move = self.neighbour_deduction.find_move()
        if move:
            action, row, col = move
            print("AI znalazło ruch dedukcyjny" )
            return (action, row, col)

        print("AI nie znalazło bezpiecznego ruchu, wykonuje losowy ruch.")
        random_move = self.get_random_move()
        if random_move:
            row, col = random_move
            return ('reveal', row, col)
        return None

    def get_random_move(self):
        available_moves = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col] and not self.game.flags[row][col]:
                    available_moves.append((row, col))

        if available_moves:
            return random.choice(available_moves)
        return None
