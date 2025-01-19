import random
from neighbour_deduction import NeighbourDeduction
from cluster_inference import ClusterInference
from Random_Forest_Flagging import Random_Forest
from monte_carlo_analyzer import MonteCarloAnalyzer

class AIPlayer:
    def __init__(self, game):
        self.game = game
        self._neighbour_deduction = NeighbourDeduction(game)
        self._cluster_inference = ClusterInference(game)
        self._Random_Forest_flagging = Random_Forest(game)
        self._monte_carlo_analyzer = MonteCarloAnalyzer(game)
        self.current_algorithm = None

    def make_move(self):
        move = self._neighbour_deduction.find_move()
        if move:
            self.current_algorithm = "Neighbour Deduction"
            action, row, col = move
            print(f"AI znalazło ruch dedukcyjny ({self.current_algorithm}).")
            return action, row, col

        move = self._cluster_inference.analyze_clusters()
        if move:
            self.current_algorithm = "Cluster Inference"
            action, row, col = move
            print(f"AI znalazło ruch klastrowy ({self.current_algorithm}).")
            return action, row, col

        move = self._Random_Forest_flagging.find_flag()
        if move:
            self.current_algorithm = "Random Forest"
            row, col, prob = move
            print(f"AI przewiduje pole ({row}, {col}) jako minę z prawdopodobieństwem {prob:.2f}.")
            return 'flag', row, col

        move = self._monte_carlo_analyzer.analyze()
        if move:
            self.current_algorithm = "Monte Carlo"
            row, col = move
            print(f"AI wybiera pole na podstawie Monte Carlo: ({row}, {col})")
            return ('reveal', row, col)

    def get_current_algorithm(self):
        return self.current_algorithm