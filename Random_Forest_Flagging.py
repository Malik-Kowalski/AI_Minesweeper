import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import class_weight
import pickle

class Random_Forest:
    def __init__(self, game, model_path="model.pkl", data_path='game_log_processed_data.csv'):
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

    def load_and_preprocess_data(self, file_path):
        try:
            data = pd.read_csv(file_path)
            print("Dane wczytane.")

            data = self.validate_data(data)

            self.features = data.drop(columns=["Label"]).values
            self.target = data["Label"].values

            print("Dane przetworzone.")

            unique_classes = np.unique(self.target)
            print(f"Unikalne klasy w danych: {unique_classes}")

            all_classes = np.arange(np.min(self.target), np.max(self.target) + 1)
            missing_classes = set(all_classes) - set(unique_classes)

            if missing_classes:
                print(f"Brakujące klasy: {missing_classes}. Dodawanie ich do danych.")
                for missing_class in missing_classes:
                    missing_data = np.zeros((self.target == missing_class).sum(), self.features.shape[1])
                    missing_target = np.full(missing_data.shape[0], missing_class)
                    self.features = np.vstack([self.features, missing_data])
                    self.target = np.hstack([self.target, missing_target])

        except Exception as e:
            print(f"Błąd podczas przetwarzania danych: {e}")
            self.features, self.target = None, None

    def validate_data(self, data):

        data = data.dropna()

        for col in data.columns:
            if not pd.to_numeric(data[col], errors='coerce').notnull().all():
                print(f"Kolumna {col} zawiera niepoprawne dane. Usuwam te wiersze.")
                data = data[pd.to_numeric(data[col], errors='coerce').notnull()]

        return data

    def train_model(self):
        if self.features is None or self.target is None:
            print("Brak przetworzonych danych. Nie można wytrenować modelu.")
            return

        try:
            class_weights = class_weight.compute_class_weight(
                class_weight="balanced",
                classes=np.unique(self.target),
                y=self.target
            )
            class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}

            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight=class_weights_dict
            )

            self.model.fit(self.features, self.target)
            print("Model został wytrenowany z balansem klas.")

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
                print("Model wczytany.")
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
            flat_matrix = np.ravel(adjacent_matrix).reshape(1, -1)
            prediction_proba = self.model.predict_proba(flat_matrix)
            return prediction_proba[0][1]

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
                        prob_flagging = self.predict(adjacent_matrix)
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
                    row_data.append(-4)
            adjacent_matrix.append(row_data)
        print(f"Macierz dla ({row}, {col}): {adjacent_matrix}")
        return adjacent_matrix

    def find_flag(self):
        flagged_fields = self.predict_game_state(self.game)
        if flagged_fields:
            flagged_fields = [(row, col, prob) for row, col, prob in flagged_fields if prob > 0.7]

            if flagged_fields:
                for idx, (row, col, prob) in enumerate(flagged_fields):
                    discovered_neighbors = self.count_discovered_neighbors(row, col)
                    flagged_fields[idx] = (row, col, prob, discovered_neighbors)

                flagged_fields.sort(key=lambda x: (x[2], x[3]), reverse=True)

                row, col, prob, discovered_neighbors = flagged_fields[0]
                print(
                    f"Pole ({row}, {col}) z {discovered_neighbors} odkrytymi sąsiednimi polami ma prawdopodobieństwo: {prob:.2f}")
                return row, col, prob
        return None

    def count_discovered_neighbors(self, row, col):

        discovered_neighbors = 0
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if 0 <= i < self.game.rows and 0 <= j < self.game.cols:
                    if self.game.revealed[i][j]:
                        discovered_neighbors += 1
        return discovered_neighbors

