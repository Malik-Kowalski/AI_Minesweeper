from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
import sys
from minesweeper import Minesweeper
from ai_player import AIPlayer
from GameLogger import GameLogger
from game_results_logger import GameResultsLogger

class GameGeneratorMinesweeperGUI(QMainWindow):
    def __init__(self, game, ai_player, games_to_play, rows, cols, mines):
        super().__init__()
        self.game = game
        self.ai_player = ai_player
        self._logger = GameLogger("game_log.csv")
        self._results_logger = GameResultsLogger("game_results.xlsx")
        self._logger.start_new_game()
        self.games_to_play = games_to_play
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self._results_logger.start_new_game(self._logger.game_id, game.rows, game.cols, game.mines)
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("Minesweeper")
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)
        self._grid = QGridLayout(self._central_widget)
        self._buttons = {}

        for row in range(self.game.rows):
            for col in range(self.game.cols):
                button = QPushButton(" ")
                button.setFixedSize(30, 30)
                button.setStyleSheet("background-color: gray;")
                button.clicked.connect(lambda _, r=row, c=col: self._on_click(r, c))
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda _, r=row, c=col: self._on_right_click(r, c))
                self._grid.addWidget(button, row, col)
                self._buttons[(row, col)] = button

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._play_ai_move)
        self._timer.start(0)

    def _on_click(self, row, col):
        try:
            result = self.game.reveal(row, col)
            self._logger.log_move("reveal", row, col, result, self.game)
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
            self.game.flag(row, col)
            self._logger.log_move("flag", row, col, "AI_flagged", self.game)
            self._update_board()
        except Exception as e:
            print(f"Error in on_right_click: {e}")

    def _update_board(self):
        try:
            for row in range(self.game.rows):
                for col in range(self.game.cols):
                    button = self._buttons[(row, col)]
                    if self.game.flags[row][col]:
                        button.setText("F")
                        button.setStyleSheet("color: red; background-color: gray;")
                    elif self.game.revealed[row][col]:
                        if self.game.board[row][col] == -1:
                            button.setText("*")
                            button.setStyleSheet("color: black; background-color: darkgray;")
                        else:
                            button.setText(str(self.game.board[row][col]) if self.game.board[row][col] > 0 else " ")
                            button.setStyleSheet("color: blue; background-color: darkgray;")
                    else:
                        button.setText(" ")
                        button.setStyleSheet("background-color: gray;")
        except Exception as e:
            print(f"Error in update_board: {e}")

    def _show_game_over(self):
        print("Game Over!")
        self._results_logger.finalize_results("Loss")
        self._end_game()

    def _show_win_message(self):
        print("Congratulations! You've won the game!")
        self._results_logger.finalize_results("Win")
        self._end_game()

    def _end_game(self):
        self._timer.stop()
        self.games_to_play -= 1
        if self.games_to_play > 0:
            self._start_new_game()
        else:
            self.quit_game()

    def _start_new_game(self):
        new_game = Minesweeper(self.rows, self.cols, self.mines)
        new_ai_player = AIPlayer(new_game)
        self.game = new_game
        self.ai_player = new_ai_player
        self._logger.start_new_game()
        self._results_logger.start_new_game(self._logger.game_id, self.rows, self.cols, self.mines)
        self._update_board()
        self._timer.start(0)

    def _play_ai_move(self):
        try:
            move = self.ai_player.make_move()
            if move:
                action, row, col = move
                algorithm = self.ai_player.get_current_algorithm()
                self._results_logger.log_move(algorithm)
                if action == 'reveal':
                    print(f"AI odkrywa: {row}, {col}")
                    self._on_click(row, col)
                elif action == 'flag':
                    print(f"AI flaguje: {row}, {col}")
                    self._on_right_click(row, col)
            else:
                print("AI nie ma dostępnych ruchów.")
                self._timer.stop()
        except Exception as e:
            print(f"Error in play_ai_move: {e}")

    def quit_game(self):
        print("All games are finished.")
        self.close()


def run_game(games_to_play=5, rows=10, cols=10, mines=10):
    try:
        app = QApplication(sys.argv)
        game = Minesweeper(rows, cols, mines)
        ai_player = AIPlayer(game)
        gui = GameGeneratorMinesweeperGUI(game, ai_player, games_to_play, rows, cols, mines)
        gui.show()
        app.exec_()
    except Exception as e:
        print(f"Error in main: {e}")


run_game(games_to_play=10, rows=10, cols=10, mines=10)
