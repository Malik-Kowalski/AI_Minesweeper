import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QGridLayout, QWidget
from PyQt5.QtCore import Qt

class Minesweeper:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flags = [[False for _ in range(cols)] for _ in range(rows)]
        self._place_mines()
        self._calculate_numbers()

    def _place_mines(self):
        placed_mines = 0
        while placed_mines < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.board[row][col] == 0:
                self.board[row][col] = -1
                placed_mines += 1

    def reveal(self, row, col):
        if self.revealed[row][col] or self.flags[row][col]:
            return
        self.revealed[row][col] = True
        if self.board[row][col] == -1:
            return "game_over"
        elif self.board[row][col] == 0:
            self._reveal_neighbors(row, col)
        if self.check_win():
            return "win"
        return "safe"

    def flag(self, row, col):
        if not self.revealed[row][col]:
            self.flags[row][col] = not self.flags[row][col]

    def _reveal_neighbors(self, row, col):
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if 0 <= r < self.rows and 0 <= c < self.cols and not self.revealed[r][c]:
                    self.reveal(r, c)

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1 and not self.revealed[row][col]:
                    return False
        return True

    def _calculate_numbers(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == -1:
                    continue
                mine_count = 0
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == -1:
                            mine_count += 1
                self.board[row][col] = mine_count

class MinesweeperGUI(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    rows, cols, mines = 8, 8, 10
    game = Minesweeper(rows, cols, mines)
    gui = MinesweeperGUI(game)
    gui.show()
    sys.exit(app.exec_())