import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QGridLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from minesweeper import Minesweeper
from ai_player import AIPlayer

class MinesweeperGUI(QMainWindow):
    def __init__(self, game, ai_player):
        super().__init__()
        self.game = game
        self.ai_player = ai_player
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Minesweeper")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid = QGridLayout(self.central_widget)
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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_ai_move)
        self.timer.start(1000)

    def on_click(self, row, col):
        result = self.game.reveal(row, col)
        if result == "game_over":
            self.show_game_over()
        elif result == "win":
            self.show_win_message()
        else:
            self.update_board()

    def on_right_click(self, row, col):
        self.game.flag(row, col)
        self.update_board()

    def update_board(self):
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                button = self.buttons[(row, col)]
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

    def show_game_over(self):
        QMessageBox.critical(self, "Game Over", "You hit a mine! Game Over.")
        self.close()

    def show_win_message(self):
        QMessageBox.information(self, "Congratulations!", "You've won the game!")
        self.close()

    def play_ai_move(self):
        safe_move = self.ai_player.make_move()
        if safe_move:
            row, col = safe_move
            print(f"AI wykonuje ruch: ({row}, {col})")
            self.on_click(row, col)
        else:
            print("AI nie ma dostępnych ruchów.")
            self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    rows, cols, mines = 8, 8, 10
    game = Minesweeper(rows, cols, mines)
    ai_player = AIPlayer(game)
    gui = MinesweeperGUI(game, ai_player)
    gui.show()
    sys.exit(app.exec_())
