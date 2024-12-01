import pandas as pd
import os

class GameResultsLogger:
    def __init__(self, filename="game_results.xlsx"):
        self.filename = filename
        self.current_game = None
        self.results = {
            'GameID': None,
            'Mines': 0,
            'BoardSize': None,
            'TotalMoves': 0,
            'NeighbourDeductionMoves': 0,
            'ClusterInferenceMoves': 0,
            'BayesianMoves': 0,
            'MonteCarloMoves': 0,
            'NeighbourDeductionPercentage': 0.0,
            'ClusterInferencePercentage': 0.0,
            'BayesianPercentage': 0.0,
            'MonteCarloPercentage': 0.0,
            'Result': None
        }
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.isfile(self.filename):
            columns = [
                'GameID', 'Mines', 'BoardSize', 'TotalMoves',
                'NeighbourDeductionMoves', 'ClusterInferenceMoves',
                'BayesianMoves', 'MonteCarloMoves',
                'NeighbourDeductionPercentage', 'ClusterInferencePercentage',
                'BayesianPercentage', 'MonteCarloPercentage', 'Result'
            ]
            df = pd.DataFrame(columns=columns)
            try:
                df.to_excel(self.filename, index=False, engine='openpyxl')
                print(f"Plik {self.filename} utworzony pomyślnie.")
            except Exception as e:
                print(f"Błąd podczas tworzenia pliku Excel: {e}")

    def start_new_game(self, game_id, rows, cols, mines):
        self.current_game = game_id
        self.results['GameID'] = game_id
        self.results['Mines'] = mines
        self.results['BoardSize'] = f"{rows}x{cols}"

    def log_move(self, algorithm):
        self.results['TotalMoves'] += 1
        if algorithm == "Neighbour Deduction":
            self.results['NeighbourDeductionMoves'] += 1
        elif algorithm == "Cluster Inference":
            self.results['ClusterInferenceMoves'] += 1
        elif algorithm == "Bayesian":
            self.results['BayesianMoves'] += 1
        elif algorithm == "Monte Carlo":
            self.results['MonteCarloMoves'] += 1

    def finalize_results(self, result):
        self.results['Result'] = result
        if self.results['TotalMoves'] > 0:
            self.results['NeighbourDeductionPercentage'] = (self.results['NeighbourDeductionMoves'] / self.results['TotalMoves']) * 100
            self.results['ClusterInferencePercentage'] = (self.results['ClusterInferenceMoves'] / self.results['TotalMoves']) * 100
            self.results['BayesianPercentage'] = (self.results['BayesianMoves'] / self.results['TotalMoves']) * 100
            self.results['MonteCarloPercentage'] = (self.results['MonteCarloMoves'] / self.results['TotalMoves']) * 100

        self.save_results()

    def save_results(self):
        try:
            if os.path.isfile(self.filename):
                existing_data = pd.read_excel(self.filename, engine='openpyxl')
            else:
                existing_data = pd.DataFrame()

            new_data = pd.DataFrame([self.results])

            existing_data = existing_data.dropna(axis=1, how='all')
            new_data = new_data.dropna(axis=1, how='all')

            updated_data = pd.concat([existing_data, new_data], ignore_index=True)

            updated_data.to_excel(self.filename, index=False, engine='openpyxl')
            print(f"Wyniki zapisane do {self.filename}")
        except Exception as e:
            print(f"Błąd podczas zapisywania wyników do Excela: {e}")
