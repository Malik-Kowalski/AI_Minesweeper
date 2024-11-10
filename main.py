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
        self.timer.start(2000)

    def on_click(self, row, col):
        try:
            print(f"Kliknięto pole ({row}, {col})")
            result = self.game.reveal(row, col)
            print(f"Wynik odkrycia: {result}")
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
            print(f"Prawy klik na polu ({row}, {col})")
            self.game.flag(row, col)
            self.update_board()
        except Exception as e:
            print(f"Error in on_right_click: {e}")

    def update_board(self):
        try:
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
        except Exception as e:
            print(f"Error in update_board: {e}")

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
                action, row, col = move
                if action == 'reveal':
                    print(f"AI wykonuje ruch odkrywania na ({row}, {col})")
                    self.on_click(row, col)
                elif action == 'flag':
                    print(f"AI flaguje pole na ({row}, {col})")
                    self.on_right_click(row, col)
            else:
                print("AI nie ma dostępnych ruchów.")
                self.timer.stop()
        except Exception as e:
            print(f"Error in play_ai_move: {e}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        rows, cols, mines = 8, 8, 10
        game = Minesweeper(rows, cols, mines)
        ai_player = AIPlayer(game)
        gui = MinesweeperGUI(game, ai_player)
        gui.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error in main: {e}")
