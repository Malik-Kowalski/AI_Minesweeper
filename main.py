import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QMessageBox, QGridLayout, QWidget,
    QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QSpinBox, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer
from minesweeper import Minesweeper
from ai_player import AIPlayer
from GameLogger import GameLogger
from game_results_logger import GameResultsLogger


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("Minesweeper - Start")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        size_layout = QHBoxLayout()
        size_label = QLabel("Board Size:")
        self._size_combo = QComboBox()
        self._size_combo.addItems(["10 x 10", "25 x 25", "25 x 40"])
        size_layout.addWidget(size_label)
        size_layout.addWidget(self._size_combo)
        layout.addLayout(size_layout)
        mines_layout = QHBoxLayout()
        mines_label = QLabel("Mines:")
        self._mines_spinbox = QSpinBox()
        self._mines_spinbox.setMinimum(1)
        self._mines_spinbox.setValue(10)
        mines_layout.addWidget(mines_label)
        mines_layout.addWidget(self._mines_spinbox)
        layout.addLayout(mines_layout)

        delay_layout = QHBoxLayout()
        delay_label = QLabel("AI Delay:")
        self._delay_combo = QComboBox()
        self._delay_combo.addItems(["0s", "1s", "2s", "3s"])
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self._delay_combo)
        layout.addLayout(delay_layout)

        start_button = QPushButton("Start Game", self)
        start_button.clicked.connect(self._start_game)
        layout.addWidget(start_button)

        self._size_combo.currentTextChanged.connect(self._update_mines_limit)

    def _update_mines_limit(self):
        size = self._size_combo.currentText().split(" x ")
        max_mines = int(size[0]) * int(size[1])
        self._mines_spinbox.setMaximum(max_mines)

    def _start_game(self):
        size_text = self._size_combo.currentText()
        rows, cols = map(int, size_text.split(" x "))

        mines = self._mines_spinbox.value()

        delay_text = self._delay_combo.currentText()
        delay = int(delay_text[:-1])

        self.close()
        game = Minesweeper(rows, cols, mines)
        ai_player = AIPlayer(game)
        self._gui = MinesweeperGUI(game, ai_player, delay)
        self._gui.show()


class MinesweeperGUI(QMainWindow):
    def __init__(self, game, ai_player, delay):
        super().__init__()
        self._game = game
        self._ai_player = ai_player
        self._logger = GameLogger("game_log.csv")
        self._results_logger = GameResultsLogger("game_results.xlsx")
        self._logger.start_new_game()
        self._delay = delay * 1000
        self._highlighted_cell = None
        self._results_logger.start_new_game(
            self._logger.game_id, game.rows, game.cols, game.mines
        )
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("Minesweeper")
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)

        main_layout = QHBoxLayout(self._central_widget)
        game_layout = QVBoxLayout()
        main_layout.addLayout(game_layout)

        self._algorithms = {
            "Neighbour Deduction": QLabel("Neighbour Deduction"),
            "Cluster Inference": QLabel("Cluster Inference"),
            "Random Forest": QLabel("Random Forest"),
            "Monte Carlo": QLabel("Monte Carlo"),
        }
        for label in self._algorithms.values():
            label.setStyleSheet("color: gray; font-weight: normal;")
            game_layout.addWidget(label)

        self._grid = QGridLayout()
        game_layout.addLayout(self._grid)
        self._buttons = {}

        for row in range(self._game.rows):
            for col in range(self._game.cols):
                button = QPushButton(" ")
                button.setFixedSize(30, 30)
                button.setStyleSheet("background-color: gray;")
                button.clicked.connect(lambda _, r=row, c=col: self._on_click(r, c))
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(
                    lambda _, r=row, c=col: self._on_right_click(r, c)
                )
                self._grid.addWidget(button, row, col)
                self._buttons[(row, col)] = button

        self._history_browser = QTextBrowser(self)
        self._history_browser.setFixedWidth(300)
        main_layout.addWidget(self._history_browser)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._play_ai_move)
        self._timer.start(self._delay)

    def _on_click(self, row, col):
        try:
            self._toggle_highlight(row, col)
            result = self._game.reveal(row, col)
            self._logger.log_move("reveal", row, col, result, self._game)
            self._history_browser.append(f"Revealed: ({row}, {col}) Result: {result}")
            if result == "game_over":
                self._show_game_over()
            elif result == "win":
                self._show_win_message()
            else:
                self._update_board()
        except Exception as e:
            print(f"Error in on_click: {e}")

    def _on_right_click(self, row, col):
        try:
            self._toggle_highlight(row, col)
            self._game.flag(row, col)
            self._logger.log_move("flag", row, col, "AI_flagged", self._game)
            self._history_browser.append(f"Flagged: ({row}, {col})")
            self._update_board()
        except Exception as e:
            print(f"Error in on_right_click: {e}")

    def _toggle_highlight(self, row, col):
        if self._highlighted_cell == (row, col):
            self._highlighted_cell = None
        else:
            self._highlighted_cell = (row, col)
        self._update_board()

    def _update_board(self):
        try:
            for row in range(self._game.rows):
                for col in range(self._game.cols):
                    button = self._buttons[(row, col)]
                    if self._game.flags[row][col]:
                        button.setText("F")
                        button.setStyleSheet("color: red; background-color: gray; font-weight: bold;")
                    elif self._game.revealed[row][col]:
                        if self._game.board[row][col] == -1:
                            button.setText("*")
                            button.setStyleSheet("color: black; background-color: darkgray; font-weight: bold;")
                        else:
                            number = self._game.board[row][col]
                            button.setText(str(number) if number > 0 else " ")
                            color = self._get_number_color(number)
                            button.setStyleSheet(f"color: {color}; background-color: darkgray; font-weight: bold;")
                    else:
                        button.setText(" ")
                        button.setStyleSheet("background-color: gray; font-weight: bold;")

            if self._highlighted_cell:
                row, col = self._highlighted_cell
                button = self._buttons[(row, col)]
                original_color = self._get_original_color(row, col)
                button.setStyleSheet(f"color: {original_color}; background-color: lightblue; font-weight: bold;")
        except Exception as e:
            print(f"Error in update_board: {e}")

    def _get_original_color(self, row, col):
        if self._game.flags[row][col]:
            return "red"
        if self._game.revealed[row][col]:
            value = self._game.board[row][col]
            if value == -1:
                return "black"
            return self._get_number_color(value)
        return "black"

    def _get_number_color(self, number):
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

    def _show_game_over(self):
        print("Game Over!")
        QMessageBox.critical(self, "Game Over", "You hit a mine! Game Over.")
        self._results_logger.finalize_results("Loss")
        self._timer.stop()
        self.close()

    def _show_win_message(self):
        print("Congratulations! You've won the game!")
        QMessageBox.information(self, "Congratulations!", "You've won the game!")
        self._results_logger.finalize_results("Win")
        self._timer.stop()
        self.close()

    def _play_ai_move(self):
        try:
            move = self._ai_player.make_move()
            if move:
                action, row, col = move
                algorithm = self._ai_player.get_current_algorithm()
                self._update_algorithm_status(algorithm)
                self._results_logger.log_move(algorithm)
                if action == 'reveal':
                    self._on_click(row, col)
                elif action == 'flag':
                    self._on_right_click(row, col)
            else:
                print("AI nie ma dostępnych ruchów.")
                self._timer.stop()
        except Exception as e:
            print(f"Error in play_ai_move: {e}")

    def _update_algorithm_status(self, algorithm):
        for key, label in self._algorithms.items():
            if key == algorithm:
                label.setStyleSheet("color: green; font-weight: bold;")
            else:
                label.setStyleSheet("color: gray; font-weight: normal;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec_())
