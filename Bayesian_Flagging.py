import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.ensemble import RandomForestClassifier
import pickle
from collections import Counter


class Bayesian:
    def __init__(self, game, model_path="model.pkl", data_path='game_log.csv'):
        self.game = game
        self.model_path = model_path
        self.model = None
        self.features = None
        self.target = None

        if not self.load_model():
            print("Nie znaleziono zapisanego modelu. Rozpoczynam proces nauki.")
            if data_path:
                self.load_and_preprocess_data(data_path)
                self.train_model()
            else:
                print("Brak ścieżki do danych treningowych. Model nie może być wytrenowany.")

    def preprocess_adjacent(self, matrix_str):

        try:
            matrix = literal_eval(matrix_str)
            for i in range(3):
                for j in range(3):
                    if matrix[i][j] is None:
                        matrix[i][j] = -3
                    elif matrix[i][j] == 'F':
                        matrix[i][j] = -2

            matrix[1][1] = -3

            return matrix
        except Exception as e:
            print(f"Błąd podczas przetwarzania macierzy: {e}")
            return None

    def load_and_preprocess_data(self, file_path):

        try:
            data = pd.read_csv(file_path)
            print("Dane wczytane.")

            data['Adjacent3x3'] = data['Adjacent3x3'].apply(self.preprocess_adjacent)
            data = data.dropna(subset=['Adjacent3x3'])

            result_mapping = {'safe': 0, 'win': 0, 'AI_flagged': 1, 'game_over': 1}
            print("Unikalne wartości w 'Result' przed mapowaniem:", data['Result'].unique())
            data['Result'] = data['Result'].map(result_mapping)

            print("Rozkład wartości po mapowaniu:")
            print(data['Result'].value_counts(dropna=False))

            data = data.dropna(subset=['Result'])

            data = data[data['Adjacent3x3'].apply(lambda x: len(x) == 3 and all(len(row) == 3 for row in x))]

            self.features = np.array([np.ravel(matrix) for matrix in data['Adjacent3x3']])

            self.target = data['Result'].values

            print("Rozkład klas w danych treningowych:", Counter(self.target))
            print("Dane przetworzone.")

        except Exception as e:
            print(f"Błąd podczas przetwarzania danych: {e}")
            self.features, self.target = None, None

    def train_model(self):

        if self.features is None or self.target is None:
            print("Brak przetworzonych danych. Nie można wytrenować modelu.")
            return

        try:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)

            self.model.fit(self.features, self.target)
            print("Model został wytrenowany.")

            self.save_model()

        except Exception as e:
            print(f"Błąd podczas trenowania modelu: {e}")

    def save_model(self):
        try:
            with open(self.model_path, "wb") as file:
                pickle.dump(self.model, file)
                print(f"Model zapisany do pliku: {self.model_path}")
        except Exception as e:
            print(f"Błąd podczas zapisywania modelu: {e}")

    def load_model(self):

        try:
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
                print("Model Bayesian wczytany.")
                return True
        except FileNotFoundError:
            print(f"Plik {self.model_path} nie istnieje. Trzeba wytrenować model.")
        except Exception as e:
            print(f"Błąd podczas wczytywania modelu: {e}")
        return False

    def predict(self, adjacent_matrix):

        if self.model is None:
            print("Model nie został wczytany. Nie można dokonać predykcji.")
            return None

        try:
            processed_matrix = self.preprocess_adjacent(adjacent_matrix)
            if processed_matrix is None:
                print("Błędna macierz wejściowa.")
                return None

            flat_matrix = np.ravel(processed_matrix).reshape(1, -1)
            prediction = self.model.predict(flat_matrix)
            return prediction[0]
        except Exception as e:
            print(f"Błąd podczas predykcji: {e}")
            return None

    def predict_game_state(self, game):

        flagged_fields = []
        for row in range(game.rows):
            for col in range(game.cols):
                if not game.revealed[row][col] and not game.flags[row][col]:
                    adjacent_matrix = self.get_adjacent_3x3(game, row, col)
                    if adjacent_matrix is not None:
                        matrix_str = str(adjacent_matrix)
                        print(f"Przewidywanie dla pola ({row}, {col}) z danymi: {matrix_str}")
                        prob_flagging = self.predict(matrix_str)
                        print(f"Prawdopodobieństwo flagowania dla ({row}, {col}): {prob_flagging}")
                        flagged_fields.append((row, col, prob_flagging))

        return flagged_fields

    def get_adjacent_3x3(self, game, row, col):

        adjacent_matrix = []
        for i in range(row - 1, row + 2):
            row_data = []
            for j in range(col - 1, col + 2):
                if 0 <= i < game.rows and 0 <= j < game.cols:
                    if game.revealed[i][j]:
                        row_data.append(game.board[i][j])
                    elif game.flags[i][j]:
                        row_data.append(-2)
                    else:
                        row_data.append(-3)
                else:
                    row_data.append(-3)
            adjacent_matrix.append(row_data)
        print(f"Macierz dla ({row}, {col}): {adjacent_matrix}")
        return adjacent_matrix

    def find_flag(self):

        flagged_fields = self.predict_game_state(self.game)
        if flagged_fields:
            flagged_fields = [(row, col, prob) for row, col, prob in flagged_fields if prob > 0.5]

            if flagged_fields:
                flagged_fields.sort(key=lambda x: x[2], reverse=True)
                row, col, prob = flagged_fields[0]
                print(f"Pole ({row}, {col}) prawdopodobieństwo: {prob:.2f}")
                return row, col, prob
        return None

