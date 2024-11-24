import os
import pickle
import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB


class BayesianInference:
    def __init__(self, game, log_file="game_log.csv", model_file="naive_bayes_model.pkl"):
        self.game = game
        self.log_file = log_file
        self.model_file = model_file
        self.model = GaussianNB()
        self.train_data = None
        self.train_labels = None
        self.trained = False

        if os.path.exists(self.model_file):
            self.load_model()
            print("Model załadowany pomyślnie.")
        else:
            print("Brak modelu, rozpoczynam trening.")
            self.load_training_data()
            self.train_model()

    def load_training_data(self):
        if os.path.isfile(self.log_file):
            data = pd.read_csv(self.log_file)
            if not data.empty:
                self.train_data = []
                self.train_labels = []

                for _, row in data.iterrows():
                    if row['Result'] in ['safe', 'mine']:
                        label = 1 if row['Result'] == 'mine' else 0
                        adjacent = eval(row['Adjacent3x3'])
                        flattened = []

                        for row_data in adjacent:
                            for value in row_data:
                                if value is None:
                                    flattened.append(-1)
                                elif value == 'F':
                                    flattened.append(-2)
                                else:
                                    try:
                                        flattened.append(float(value))
                                    except ValueError:
                                        flattened.append(0)

                        self.train_data.append(flattened)
                        self.train_labels.append(label)

                if self.train_data:
                    self.train_data = np.array(self.train_data)
                    self.train_labels = np.array(self.train_labels)

    def train_model(self):
        try:
            if np.any(np.isnan(self.train_data)) or np.any(np.isnan(self.train_labels)):
                print("Dane zawierają NaN!")
                return
            if np.any(np.isinf(self.train_data)) or np.any(np.isinf(self.train_labels)):
                print("Dane zawierają inf!")
                return

            print(f"Rozpoczynam trenowanie modelu z danymi: {self.train_data.shape} i etykietami: {self.train_labels.shape}")
            self.model.fit(self.train_data, self.train_labels)
            print("Model wytrenowany pomyślnie.")
            self.save_model()
            self.trained = True
        except Exception as e:
            print(f"Błąd podczas trenowania modelu: {e}")

    def save_model(self):
        try:
            with open(self.model_file, "wb") as f:
                pickle.dump(self.model, f)
            print("Model zapisany pomyślnie.")
        except Exception as e:
            print(f"Problem z zapisem modelu: {e}")

    def load_model(self):
        try:
            with open(self.model_file, "rb") as f:
                self.model = pickle.load(f)
            self.trained = True
            print("Model załadowany pomyślnie.")
        except Exception as e:
            print(f"Problem z ładowaniem modelu: {e}")
            self.trained = False

    def get_adjacent_3x3(self, row, col):
        adjacent_3x3 = []
        for r in range(row - 1, row + 2):
            row_data = []
            for c in range(col - 1, col + 2):
                if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
                    if self.game.revealed[r][c]:
                        row_data.append(self.game.board[r][c])
                    elif self.game.flags[r][c]:
                        row_data.append(-2)
                    else:
                        row_data.append(-1)
                else:
                    row_data.append(-1)
            adjacent_3x3.append(row_data)
        return adjacent_3x3

    def predict(self, adjacent_3x3):
        flattened = [item if item is not None else -1 for sublist in adjacent_3x3 for item in sublist]
        if len(flattened) != self.model.n_features_in_:
            print(f"Nieprawidłowy rozmiar danych wejściowych: {len(flattened)} != {self.model.n_features_in_}")
            return 0, 0
        probability = self.model.predict_proba([flattened])[0]
        prediction = self.model.predict([flattened])[0]
        return prediction, probability[1]

    def find_flag(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self.game.revealed[row][col] and not self.game.flags[row][col]:
                    adjacent = self.get_adjacent_3x3(row, col)
                    prediction, probability = self.predict(adjacent)
                    if prediction == 1 and probability > 0.8:
                        print(f"NaiveBayesInference: Oznaczam pole ({row}, {col}) jako minę (p={probability:.2f}).")
                        return 'flag', row, col
        print("NaiveBayesInference: Nie znalazłem ruchu.")
        return None
