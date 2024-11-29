import random
from neighbour_deduction import NeighbourDeduction
from cluster_inference import ClusterInference
from Bayesian_Flagging import Bayesian
from monte_carlo_analyzer import MonteCarloAnalyzer

class AIPlayer:
    def __init__(self, game):
        self.game = game
        self.neighbour_deduction = NeighbourDeduction(game)
        self.cluster_inference = ClusterInference(game)
        self.bayesian_flagging = Bayesian(game)
        self.monte_carlo_analyzer = MonteCarloAnalyzer(game)
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

        move = self.bayesian_flagging.find_flag()
        if move:
            self.current_algorithm = "Bayesian"
            row, col, prob = move
            print(f"AI przewiduje pole ({row}, {col}) jako minę z prawdopodobieństwem {prob:.2f}.")
            return 'flag', row, col

        move = self.monte_carlo_analyzer.analyze()
        if move:
            self.current_algorithm = "Monte Carlo"
            row, col = move
            print(f"AI wybiera pole na podstawie Monte Carlo: ({row}, {col})")
            return ('reveal', row, col)



    def get_current_algorithm(self):
        return self.current_algorithm