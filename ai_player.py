import random
from neighbour_deduction import NeighbourDeduction
from cluster_inference import ClusterInference
from Bayesian_Inference import BayesianInference


class AIPlayer:
    def __init__(self, game):
        self.game = game
        self.neighbour_deduction = NeighbourDeduction(game)
        self.cluster_inference = ClusterInference(game)
        self.bayesian_inference = BayesianInference(game)
        self.current_algorithm = None

    def make_move(self):
        move = self.neighbour_deduction.find_move()
        if move:
            self.current_algorithm = "Neighbour Deduction"
            action, row, col = move
            print(f"AI znalazło ruch dedukcyjny ({self.current_algorithm}).")
            return action, row, col

        move = self.cluster_inference.analyze_clusters()
        if move:
            self.current_algorithm = "Cluster Inference"
            action, row, col = move
            print(f"AI znalazło ruch klastrowy ({self.current_algorithm}).")
            return action, row, col

        move = self.bayesian_inference.find_flag()
        if move:
            self.current_algorithm = "Bayesian Inference"
            action, row, col = move
            print(f"AI znalazło oznaczenie miny ({self.current_algorithm}).")
            return action, row, col

        print("AI nie znalazło bezpiecznego ruchu, wykonuje losowy ruch.")
        self.current_algorithm = "Random Move"
        random_move = self.get_random_move()
        if random_move:
            row, col = random_move
            print(f"AI wykonuje losowy ruch na ({row}, {col}).")
            return 'reveal', row, col
        return None

    def get_random_move(self):
        available_moves = [
            (row, col) for row in range(self.game.rows) for col in range(self.game.cols)
            if not self.game.revealed[row][col] and not self.game.flags[row][col]
        ]
        return random.choice(available_moves) if available_moves else None

    def get_current_algorithm(self):
        return self.current_algorithm
