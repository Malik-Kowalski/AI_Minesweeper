import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QMessageBox, QGridLayout, QWidget,
    QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QSpinBox, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer
from minesweeper import Minesweeper
from ai_player import AIPlayer
from GameLogger import GameLogger

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Minesweeper - Start")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        size_layout = QHBoxLayout()
        size_label = QLabel("Board Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["10 x 10", "25 x 25", "25 x 40"])
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)
        mines_layout = QHBoxLayout()
        mines_label = QLabel("Mines:")
        self.mines_spinbox = QSpinBox()
        self.mines_spinbox.setMinimum(1)
        self.mines_spinbox.setValue(10)
        mines_layout.addWidget(mines_label)
        mines_layout.addWidget(self.mines_spinbox)
        layout.addLayout(mines_layout)

        delay_layout = QHBoxLayout()
        delay_label = QLabel("AI Delay:")
        self.delay_combo = QComboBox()
        self.delay_combo.addItems(["0s", "1s", "2s", "3s"])
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_combo)
        layout.addLayout(delay_layout)

        start_button = QPushButton("Start Game", self)
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button)

        self.size_combo.currentTextChanged.connect(self.update_mines_limit)

    def update_mines_limit(self):
        size = self.size_combo.currentText().split(" x ")
        max_mines = int(size[0]) * int(size[1])
        self.mines_spinbox.setMaximum(max_mines)

    def start_game(self):
        size_text = self.size_combo.currentText()
        rows, cols = map(int, size_text.split(" x "))

        mines = self.mines_spinbox.value()

        delay_text = self.delay_combo.currentText()
        delay = int(delay_text[:-1])

        self.close()
        game = Minesweeper(rows, cols, mines)
        ai_player = AIPlayer(game)
        self.gui = MinesweeperGUI(game, ai_player, delay)
        self.gui.show()


class MinesweeperGUI(QMainWindow):
    def __init__(self, game, ai_player, delay):
        super().__init__()
        self.game = game
        self.ai_player = ai_player
        self.logger = GameLogger("game_log.csv")
        self.logger.start_new_game()
        self.delay = delay * 1000
        self.highlighted_cell = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Minesweeper")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        game_layout = QVBoxLayout()
        main_layout.addLayout(game_layout)

        self.algorithms = {
            "Neighbour Deduction": QLabel("Neighbour Deduction"),
            "Cluster Inference": QLabel("Cluster Inference"),
            "Bayesian ": QLabel("Bayesian"),
            "Monte Carlo": QLabel("Monte Carlo")
        }
        for label in self.algorithms.values():
            label.setStyleSheet("color: gray; font-weight: normal;")
            game_layout.addWidget(label)

        self.grid = QGridLayout()
        game_layout.addLayout(self.grid)
        self.buttons = {}

        for row in range(self.game.rows):
            for col in range(self.game.cols):
                button = QPushButton(" ")
                button.setFixedSize(30, 30)
                button.setStyleSheet("background-color: gray;")
                button.clicked.connect(lambda _, r=row, c=col: self.on_click(r, c))
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda _, r=row, c=col: self.on_right_click(r, c))
                self.grid.addWidget(button, row, col)
                self.buttons[(row, col)] = button

        self.history_browser = QTextBrowser(self)
        self.history_browser.setFixedWidth(300)
        main_layout.addWidget(self.history_browser)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_ai_move)
        self.timer.start(self.delay)

    def on_click(self, row, col):
        try:
            self.toggle_highlight(row, col)
            result = self.game.reveal(row, col)
            self.logger.log_move("reveal", row, col, result, self.game)
            self.history_browser.append(f"Revealed: ({row}, {col}) Result: {result}")
            if result == "game_over":
                self.show_game_over()
            elif result == "win":
                self.show_win_message()
            else:
                self.update_board()
        except Exception as e:
            print(f"Error in on_click: {e}")

    def on_right_click(self, row, col):
        try:
            self.toggle_highlight(row, col)
            self.game.flag(row, col)
            self.logger.log_move("flag", row, col, "AI_flagged", self.game)
            self.history_browser.append(f"Flagged: ({row}, {col})")
            self.update_board()
        except Exception as e:
            print(f"Error in on_right_click: {e}")

    def toggle_highlight(self, row, col):
        if self.highlighted_cell == (row, col):
            self.highlighted_cell = None
        else:
            self.highlighted_cell = (row, col)
        self.update_board()

    def update_board(self):
        try:
            for row in range(self.game.rows):
                for col in range(self.game.cols):
                    button = self.buttons[(row, col)]
                    if self.game.flags[row][col]:
                        button.setText("F")
                        button.setStyleSheet("color: red; background-color: gray; font-weight: bold;")
                    elif self.game.revealed[row][col]:
                        if self.game.board[row][col] == -1:
                            button.setText("*")
                            button.setStyleSheet("color: black; background-color: darkgray; font-weight: bold;")
                        else:
                            number = self.game.board[row][col]
                            button.setText(str(number) if number > 0 else " ")
                            color = self.get_number_color(number)
                            button.setStyleSheet(f"color: {color}; background-color: darkgray; font-weight: bold;")
                    else:
                        button.setText(" ")
                        button.setStyleSheet("background-color: gray; font-weight: bold;")

            if self.highlighted_cell:
                row, col = self.highlighted_cell
                button = self.buttons[(row, col)]
                original_color = self.get_original_color(row, col)
                button.setStyleSheet(f"color: {original_color}; background-color: lightblue; font-weight: bold;")
        except Exception as e:
            print(f"Error in update_board: {e}")

    def get_original_color(self, row, col):

        if self.game.flags[row][col]:
            return "red"
        if self.game.revealed[row][col]:
            value = self.game.board[row][col]
            if value == -1:
                return "black"
            return self.get_number_color(value)
        return "black"

    def get_number_color(self, number):
        color_map = {
            1: "blue",
            2: "green",
            3: "orange",
            4: "purple",
            5: "maroon",
            6: "turquoise",
            7: "black",
            8: "gray"
        }
        return color_map.get(number, "black")

    def show_game_over(self):
        print("Game Over!")
        QMessageBox.critical(self, "Game Over", "You hit a mine! Game Over.")
        self.timer.stop()
        self.close()

    def show_win_message(self):
        print("Congratulations! You've won the game!")
        QMessageBox.information(self, "Congratulations!", "You've won the game!")
        self.timer.stop()
        self.close()

    def play_ai_move(self):
        try:
            move = self.ai_player.make_move()
            if move:
                current_algorithm = self.ai_player.get_current_algorithm()
                self.update_algorithm_status(current_algorithm)

                action, row, col = move
                if action == 'reveal':
                    print(f"AI odkrywa: {row}, {col}")
                    self.on_click(row, col)
                elif action == 'flag':
                    print(f"AI flaguje: {row}, {col}")
                    self.on_right_click(row, col)
            else:
                print("AI nie ma dostępnych ruchów.")
                self.timer.stop()
        except Exception as e:
            print(f"Error in play_ai_move: {e}")

    def update_algorithm_status(self, algorithm):
        for key, label in self.algorithms.items():
            if key == algorithm:
                label.setStyleSheet("color: green; font-weight: bold;")
            else:
                label.setStyleSheet("color: gray; font-weight: normal;")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec_())
